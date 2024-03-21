
{% macro create_id_from_str(text) %}
    abs(('x' || substr(md5({{ text }}), 1, 16))::bit(64)::bigint)
{% endmacro %}

-- OMOP TABLE: person
--- Macro to transform 'MALE' and 'FEMALE' sex values into their concept_id
{% macro gender_concept_id(sex) %}
(CASE WHEN {{ sex }} = 'MALE' THEN 8507::int -- Male
      WHEN {{ sex }} = 'FEMALE' THEN 8532::int -- Female
      WHEN {{ sex }} is null THEN 0::int -- No data
      ELSE 8551::int -- Unknown
      END)
{% endmacro %}


-- OMOP TABLE: visit_occurrence
-- Macro to transform encounter class values into their concept_id
{% macro visit_concept_id(encounter_class) %}
(CASE {{ encounter_class }}
        WHEN 'AP' THEN 9202 -- Atenció primaria --> Outpatient Visit
        WHEN 'URG' THEN 9203 -- Urgencies --> Emergency Room Visit
        WHEN 'AH' THEN 9201 -- Atenció hospitalaria --> Inpatient Visit
        WHEN 'SMA' THEN 9202 -- Salut mental ambulatoria --> Outpatient Visit
        WHEN 'SMH' THEN 9201 -- Salut mental hospitalaria --> Outpatient Visit
        ELSE 0
        END)
{% endmacro %}

