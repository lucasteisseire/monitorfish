-- WIT catches AS (
--     SELECT
--         cfr,
--         ers_id,
--         (value)->>'gear' AS gear,
--         jsonb_array_elements((value)->'catches')->>'species' AS species,
--         (jsonb_array_elements((value)->'catches')->>'weight')::DOUBLE PRECISION AS weight,
--         jsonb_array_elements((value)->'catches')->>'faoZone' AS fao_zone
--     FROM public.ers
--     WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
--     AND operation_type = 'DAT'
--     AND log_type = 'FAR'
--     LIMIT 10000)
    
SELECT
    cfr,
    ers_id,
    trip_number,
    log_type,
    SUM(CASE WHEN log_type = 'DEP' THEN 1 ELSE 0 END) OVER (PARTITION BY cfr ORDER BY operation_datetime_utc) AS computed_trip_number
FROM public.ers
-- WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
WHERE operation_datetime_utc >= '2020-01-01'
AND operation_type = 'DAT'
AND log_type IN ('FAR', 'DEP')
AND cfr = 'FRA000278969'
LIMIT 10000