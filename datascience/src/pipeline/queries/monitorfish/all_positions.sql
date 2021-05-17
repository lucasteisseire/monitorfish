SELECT 
    internal_reference_number AS cfr, 
    date_time, 
    latitude, 
    longitude 
FROM positions 
WHERE date_time > CURRENT_TIMESTAMP - INTERVAL :within 
ORDER BY date_time;