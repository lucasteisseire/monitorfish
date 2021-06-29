SELECT
    latitude,
    longitude
FROM positions 
WHERE date_time > CURRENT_TIMESTAMP - INTERVAL '1 year' 
AND speed = 0