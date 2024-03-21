-- stg_visit_occurrence


{{ config(
   materialized='table',
   enabled=true
)
}}

WITH all_visits AS (

    SELECT * FROM {{ source('raw', 'GCAT_diagnoses_EGA') }}

),
person AS (

    SELECT * FROM {{ ref('person') }}

),
-- final_visit_ids AS (

--    SELECT * FROM {{ ref('final_visit_ids') }}

-- )

SELECT
    -- av.visit_occurrence_id AS visit_occurrence_id,
    p.person_id AS person_id,
    {{ visit_concept_id('"CMBD_ORIGIN"') }} AS visit_concept_id,
    "BIRTHDATE"::DATE AS visit_start_date,
    "BIRTHDATE"::TIMESTAMP AS visit_start_datetime,
    NULL::DATE AS visit_end_date,
    NULL::TIMESTAMP AS visit_end_datetime,
    44818518::int AS visit_type_concept_id, -- Visit derived from EHR // OR it should be ¿encounter on claim?
    NULL::int AS provider_id,
    NULL::int AS care_site_id,
    CMBD_ORIGIN::varchar(50) AS visit_source_value,
    0::int AS visit_source_concept_id,
    0::int AS admitted_from_concept_id,
    NULL::int AS admitted_from_source_value,
    null::int AS discharged_to_source_value,
    0::int AS discharged_to_concept_id,
    -- lag(visit_occurrence_id)
    -- over(partition by p.person_id
	-- order by av.visit_start_date) AS preceding_visit_occurrence_id
FROM all_visits
JOIN person p ON EGA_ID = p.person_source_value
-- WHERE visit_occurrence_id IN (SELECT DISTINCT VISIT_OCCURRENCE_ID_NEW
                              -- FROM final_visit_ids)
