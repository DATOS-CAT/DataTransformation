-- stg_person

{{ config(
    materialized='table',
	enabled=true
)
}}

with patients as (

    select * from {{ source('raw', 'GCAT_sex_bd_EGA') }}

),
person as (
    select
        {{ create_id_from_str('"EGA_ID"::text')}} AS person_id,
        {{ gender_concept_id ('"SEX"') }} AS gender_concept_id,
        date_part('year', "BIRTHDATE"::DATE)::INT AS year_of_birth,
        date_part('month', "BIRTHDATE"::DATE)::INT AS month_of_birth,
        date_part('day', "BIRTHDATE"::DATE)::INT AS day_of_birth,
        "BIRTHDATE"::TIMESTAMP AS birth_datetime,
        NULL::INT AS race_concept_id,
        NULL::INT AS ethnicity_concept_id,
        NULL::INT AS location_id,
        NULL::INT AS provider_id,
        NULL::INT AS care_site_id,
        "EGA_ID"::VARCHAR(50) AS person_source_value,
        "SEX"::VARCHAR(50) AS gender_source_value,
        0 AS gender_source_concept_id
    from patients
    where "BIRTHDATE" is not null -- Don't load patients who do not have birthdate and sex (change variable names if necessary)
    and "SEX" is not null
)
select * from person
 