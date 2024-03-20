# ELT - Meltano & DBT

## Initialization
1. *White Rabbit* to obtain the ScanReport. 
2. *Rabbit in a Hat* to generate SQL Skeleton Files that will have in the transformation.
3. Create an environment.
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4. Install meltano 
    ```
    # to avoid any issues during the installation we will update pip
    python -m pip install -U pip setuptools wheel
    python -m pip install meltano
    ```
5. Clone this repository or start from scratch. 

## Excel / csv to raw table in Postgres
### By starting from scratch
1. Create a meltano project called `DATOS-CAT` (for example). 
    ```
    meltano init DATOS-CAT
    cd DATOS-CAT
    ```
2. Open the project.
    ```
    cd DATOS-CAT
    ```
3. Now, we need Extractors (to extract data from a source) and Loaders (to load it somewhere else). Once data is loaded, we could transform it with dbt.
    There are different types of [extractors](https://hub.meltano.com/extractors/) and [loaders](https://hub.meltano.com/loaders/) available.

    We are going to use: 
    - extractor: *tap-csv*

        > NOTE: I had a lot of problems with the [tap-spreadsheets-anywhere](https://hub.meltano.com/extractors/tap-spreadsheets-anywhere) extractor. 
        The solution was to change excel files to csv

    - loader: target-postgres

    So: 
    ```
    # meltano add extractor tap-spreadsheets-anywhere
    meltano add extractor tap-csv --variant=meltano
    meltano add loader target-postgres --variant meltanolabs
    ```
    The selected extractors and loaders are reflected in the *meltano.yml* file. 

4. The *meltano.yml* file can be modified with the appropiate characteristics. It should look like this:
    ```
    version: 1
    default_environment: dev
    project_id: 792a0f58-7a4e-4ca0-8da4-256dd018a3fc
    environments:
    - name: dev
    - name: staging
    - name: prod
    plugins:
    extractors:
        - name: tap-csv
        variant: meltano
        pip_url: git+https://gitlab.com/meltano/tap-csv.git
        config:
            files:
            - entity: *filename*
                file: *path/to/the/file*
                keys:
                - *ID*
    loaders:
    - name: target-postgres
        variant: meltanolabs
        pip_url: git+https://github.com/MeltanoLabs/target-postgres.git
        config:
        host: localhost
        port: *port*
        user: postgres
        database: *database_name*
        default_target_schema: raw
    ```
    > NOTE: Remember to change what is between * * and anything else that is necessary.  

5. Create a Postres database in Docker. 
    ```
    docker run --name datoscat_test -e POSTGRES_PASSWORD=******** -e POSTGRES_USER=postgres -p 5434:5432 -v ${PWD}/postgres:/var/lib/postgresql/data -v ${PWD}/backup:/backup -d postgres
    ``` 
6. In another terminal, we are going to create the Postgres database
    ```
    docker exec -it datoscat_test bash
    root@0ad90261a64d:/# psql -h localhost -U postgres
    psql (16.0 (Debian 16.0-1.pgdg120+1))
    Type "help" for help.

    postgres=# create database datoscat_test;
    CREATE DATABASE
    postgres=# 
    ```
7. We are going to create a .env file to store the Postres password.
    ```
    echo 'export TARGET_POSTGRES_PASSWORD=********' > .env
    ```
8. Then, we can upload the data to the postgres database using the following command 
    ```
    meltano run tap-csv target-postgres
    ```
9. Check it in DataGrip



### By cloning this repository
If you clone this repository, you already have the meltano project created. The project is called DATOS-CAT. 
1. Open the project 
    ```
    cd DATOS-CAT
    ```
2. In the *meltano.yml* file, you will se that there are Extractors (to extract data from a source) and Loaders (to load it somewhere else). Once data is loaded, we could transform it with dbt.
    There are different types of [extractors](https://hub.meltano.com/extractors/) and [loaders](https://hub.meltano.com/loaders/) available.

    The ones used are: 
    - extractor: *tap-csv*
    - loader: target-postgres

    The *meltano.yml* file can be modified with the appropiate characteristics. It should look like this:
    ```
    version: 1
    default_environment: dev
    project_id: 792a0f58-7a4e-4ca0-8da4-256dd018a3fc
    environments:
    - name: dev
    - name: staging
    - name: prod
    plugins:
    extractors:
        - name: tap-csv
        variant: meltano
        pip_url: git+https://gitlab.com/meltano/tap-csv.git
        config:
            files:
            - entity: *filename*
                file: *path/to/the/file*
                keys:
                - *ID*
    loaders:
    - name: target-postgres
        variant: meltanolabs
        pip_url: git+https://github.com/MeltanoLabs/target-postgres.git
        config:
        host: localhost
        port: *port*
        user: postgres
        database: *database_name*
        default_target_schema: raw
    ```
    > NOTE: Remember to change what is between * * and anything else that is necessary.


3. Create a Postres database in Docker. 
    ```
    docker run --name datoscat_test -e POSTGRES_PASSWORD=******** -e POSTGRES_USER=postgres -p 5434:5432 -v ${PWD}/postgres:/var/lib/postgresql/data -v ${PWD}/backup:/backup -d postgres
    ```
    
4. In another terminal, we are going to create the Postgres database
    ```
    docker exec -it datoscat_test bash
    root@0ad90261a64d:/# psql -h localhost -U postgres
    psql (16.0 (Debian 16.0-1.pgdg120+1))
    Type "help" for help.

    postgres=# create database datoscat_test;
    CREATE DATABASE
    postgres=# 
    ```
5. We are going to create a .env file to store the Postres password.
    ```
    echo 'export TARGET_POSTGRES_PASSWORD=********' > .env
    ```
6. Then, we can upload the data to the postgres database using the following command 
    ```
    meltano run tap-csv target-postgres
    ```
7. Check it in DataGrip


## Raw table to OMOP
### By starting from scratch
1. Install DBT as a Python library
    ```
    pip install dbt-postgres
    ```

2. Add a meltano transformer (but first, some packages must be uninstalled / installed) 
    ```
    python -m pip uninstall snowplow-tracker
    python -m pip uninstall minimal-snowplow-tracker
    python -m pip install snowplow-tracker
    meltano add transformer dbt-postgres
    ```

3. Configure meltano by adding the following variables to `.env`
    ```
    DBT_POSTGRES_HOST=localhost
    DBT_POSTGRES_PORT=5432
    DBT_POSTGRES_DATABASE=demo
    DBT_POSTGRES_SCHEMA=cdm
    DBT_POSTGRES_USER=postgres
    DBT_POSTGRES_PASSWORD=password
    ```
    > NOTE: Change the values!

    or by using the following commands.
    ```
    meltano config dbt-postgres list
    meltano config dbt-postgres set --interactive
    ```
4. Create the DBT models. Go to ```DATOS-CAT/transform/models``` and create a ```sources.yml``` file.
    ```
    version: 2

    sources:
    - name: raw 
        database: datoscat_test
        schema: raw
        tables:
        - name: ega_database
    ```

5. Now, go to `DATOS-CAT/transform/models`: 
    ```
    mkdir cdm 
    cd cdm
    nano person.sql
    ```

6. Create macros. Go to ```DATOS-CAT/transform/macros``` and create a ```macros.sql``` file.

7. Check that everything is right by using the following command:
    ```
    meltano invoke dbt-postgres:compile
    ```

8. To run the models, use the following command:
    ```
    meltano invoke dbt-postgres:run
    ```
9. Check it in DataGrip

### By cloning this repository
1. Install DBT as a Python library
    ```
    pip install dbt-postgres
    ```

2. Add a meltano transformer (but first, some packages must be uninstalled / installed) 
    ```
    python -m pip uninstall snowplow-tracker
    python -m pip uninstall minimal-snowplow-tracker
    python -m pip install snowplow-tracker
    meltano add transformer dbt-postgres
    ```
3. Configure meltano by adding the following variables to `.env`
    ```
    DBT_POSTGRES_HOST=localhost
    DBT_POSTGRES_PORT=5432
    DBT_POSTGRES_DATABASE=demo
    DBT_POSTGRES_SCHEMA=cdm
    DBT_POSTGRES_USER=postgres
    DBT_POSTGRES_PASSWORD=password
    ```
    > NOTE: Change the values!

    or by using the following commands.
    ```
    meltano config dbt-postgres list
    meltano config dbt-postgres set --interactive
    ```
4. The source file is already created, go to ```DATOS-CAT/transform/models``` and check ```sources.yml``` file. It should look something like this (set the parameters you need).
    ```
    version: 2

    sources:
    - name: raw 
        database: datoscat_test
        schema: raw
        tables:
        - name: ega_database
    ```

5. Then, there are also some DBT models created. Go to `DATOS-CAT/transform/models/cdm`. Here, you will see all the DBT models available.  

6. Also, the macros are created. Go to ```DATOS-CAT/transform/macros``` and check ```macros.sql``` file.

7. Check that everything is right by using the following command:
    ```
    meltano invoke dbt-postgres:compile
    ```

8. To run the models, use the following command:
    ```
    meltano invoke dbt-postgres:run
    ```
9. Check it in DataGrip



> NOTE: [Metadata](https://sdk.meltano.com/en/latest/implementation/record_metadata.html)

> NOTE: The csv files with data MUST BE separated by ','. If not it does not work, even if you specify the delimiter.