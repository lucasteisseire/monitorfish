-- The trip_number attribute is not used as it is only available for french vessels
-- A computed trip_number is made by counting DEP messages
WITH trip_numbers AS (
    SELECT
        ers_id,
        cfr,
        log_type,
        SUM(CASE WHEN log_type = 'DEP' THEN 1 ELSE 0 END) OVER (PARTITION BY cfr ORDER BY operation_datetime_utc) AS computed_trip_number
    FROM public.ers
    WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
    AND operation_type = 'DAT'
    AND log_type IN ('FAR', 'DEP')
),

far_trip_numbers AS (
    SELECT 
        ers_id, 
        cfr,
        computed_trip_number
    FROM trip_numbers
    WHERE log_type = 'FAR'
),

catches AS (
    SELECT
        ers_id,
        (value)->>'gear' AS gear,
        jsonb_array_elements((value)->'catches')->>'species' AS species,
        (jsonb_array_elements((value)->'catches')->>'weight')::DOUBLE PRECISION AS weight,
        jsonb_array_elements((value)->'catches')->>'faoZone' AS fao_area
    FROM public.ers
    WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
    AND operation_type = 'DAT'
    AND log_type = 'FAR')
    
SELECT 
    far_trip_numbers.cfr,
    far_trip_numbers.computed_trip_number,
    far_trip_numbers.ers_id,
    catches.gear,
    catches.species,
    catches.weight,
    catches.fao_area
FROM catches
FULL OUTER JOIN
far_trip_numbers
ON catches.ers_id = far_trip_numbers.ers_id