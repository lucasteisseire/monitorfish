SELECT 
    internal_reference_number AS cfr, 
    external_reference_number AS external_immatriculation, 
    ircs,
    date_time, 
    latitude, 
    longitude 
FROM positions 
WHERE date_time > CURRENT_TIMESTAMP - INTERVAL :start 
AND date_time < CURRENT_TIMESTAMP - INTERVAL :end 
ORDER BY date_time;