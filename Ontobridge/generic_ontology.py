import os
import itertools
import pandas as pd
from owlready2 import *
from owlready2 import DataProperty, ObjectProperty

datatype_range = {
    # mica key -> # ontology value
    "boolean":bool,
    "binary":bool,
    "decimal":float,
    "integer":int,
    "text":str,
    "date": datetime.date,
    "datetime": datetime.datetime,
    "None":"time",
    "": None,
}

class GenericOntology():
    def __init__(self, relative_path, data_ontology, structure_ontology, save_ontology = True):
        self.relative_path = relative_path
        self.data_ontology = data_ontology,
        self.structure_ontology = structure_ontology
        self.save_ontology = save_ontology
        
    def get_mica_dictionaries(self):
        # Get the file names
        list_mica_dict = os.listdir(self.relative_path)

        # Unique values
        list_mica_dict = list(set(list_mica_dict))

        # Remove .xlxs
        list_tables = [file.replace('.xlsx','') for file in list_mica_dict]
            
        return list_tables
    
    def read_mica_dictionaries(self, dictionary_name):
        path = os.path.join(self.relative_path, dictionary_name + '.xlsx')
        if os.path.exists(path):
            # Read variables sheet
            variables_data = pd.read_excel(path, sheet_name="Variables")

            # Read categories sheet
            categories_data = pd.read_excel(path, sheet_name="Categories")

            return variables_data, categories_data
        else:
            print("ERROR: The path and/or the file do not exist")
            pass

    def generate_ontology_structure(self):
        main_tables = {}

        def generate_main_classes():
            """
            To create the main classes.
            """
            # Data ontology (superior)
            with data_ontology:
                class Data(Thing):
                    """Separate patients from the other structure"""
                    pass

                main_tables["Data"] = Data

            # Structure ontology (inferior)
            with structure_ontology:
                class Table(Thing):
                    pass
                main_tables["Table"] = Table
                # To check the inheritance
                #print(Table.__bases__)

                class Value_range(Thing):
                    pass
                main_tables["Value_range"] = Value_range

            return Table, Value_range
            
        def generate_tables(class_table, class_value_range):

            def generate_class_tables(class_table):
                """
                One class for each table (i.e. Mica dictionary)
                """
                with structure_ontology:
                    list_tables = self.get_mica_dictionaries()
                    print("List of Mica dictionaries:", list_tables)

                    for table in list_tables:
                        if table not in main_tables:                          
                            new_class = types.new_class(table,(class_table,))
                            # To check the inheritance
                            #print((new_class.__bases__))
                            main_tables[table] = new_class    
                
                print("Main tables of the ontology", main_tables)
          
            def generate_properties_tables():
                def generate_datatype_properties(properties_list, onto_table, variables_df):
                    """
                    Each non-categorical variable is considered a data-type property. 
                    """
                    with structure_ontology:
                        for property in properties_list:
                            # The property name will be Table1_Property (e.g. demographic_Age)
                            property_name = onto_table.__name__ + "_" + property
                            
                            # Create the range
                            mica_type = list(variables_df[variables_df["name"]==property]["valueType"])
                            range_type = datatype_range[mica_type[0]]
                            
                            # Create a new property
                            new_property = type(property_name, (DataProperty,FunctionalProperty), {})
                            new_property.domain = [onto_table]
                            new_property.range = [range_type]

                        pass
            
                def generate_objecttype_properties(properties_list, onto_table, categories_df):
                    """
                    Each categorical variable is considered a object-type property. 
                    """
                    with structure_ontology:
                        for property in properties_list:
                            property_name = onto_table.__name__ + "_" + property.lower()
                            
                            # Create a new class to define the range
                            range_name = onto_table.__name__ + "_" + property.capitalize() 
                            new_class = types.new_class(range_name,(class_value_range,)) # Inherits from Value_range class.                         
                            
                            # Create a new property
                            new_property = type(property_name, (ObjectProperty,FunctionalProperty), {})
                            new_property.domain = [onto_table] # Domain: name of the table / class
                            new_property.range = new_class

                            # Create the instances
                            instance_list = list(categories_df[categories_df["variable"]==property]["name"])
                            for instance in instance_list:
                                instance_name = range_name + "_" + str(instance)
                                new_class(instance_name)
                        pass
                    
                with structure_ontology:
                    # Omits the first three tables (Data, Table, Value_range) 
                    iterator = itertools.islice(main_tables.items(), 3, None)
                    for label, onto_table in iterator:
                        variables_df, categories_df = self.read_mica_dictionaries(label)

                        # Convert both dataframes to list (important columns)
                        variables_list = list(variables_df["name"])
                        categories_list = list(categories_df["variable"].unique())

                        # Get the properties
                        datatype_properties = [variable for variable in variables_list if variable not in categories_list]
                        objecttype_properties = [variable for variable in variables_list if variable in categories_list]

                        # Generare data-type / object-type properties
                        generate_datatype_properties(datatype_properties, onto_table, variables_df)
                        generate_objecttype_properties(objecttype_properties, onto_table, categories_df)
                    pass
                
            # Generate both Class tables and Properties tables
            generate_class_tables(class_table)
            generate_properties_tables()

        def save_ontologies():
            # data_ontology.save(file="datos_redcap.owl", format="rdfxml")
            structure_ontology.save(file="estructura.owl", format="rdfxml")


        class_table, class_value_range = generate_main_classes()
        generate_tables(class_table, class_value_range)
        if self.save_ontology:
            save_ontologies()



if __name__ == '__main__':
    relative_path = r'...'
    
    # Define the main ontology URIs
    data_ontology = get_ontology("http://example_data.org/onto.owl") # Not implemented
    structure_ontology = get_ontology("http://example_structure.org/onto.owl")
    
    new_ontology = GenericOntology(
        relative_path= relative_path, 
        data_ontology = data_ontology,
        structure_ontology = structure_ontology,
        save_ontology = False
        )
    new_ontology.generate_ontology_structure()
