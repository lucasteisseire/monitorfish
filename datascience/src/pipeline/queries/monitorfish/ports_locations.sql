SELECT 
    locode, 
    latitude, 
    longitude 
FROM ports 
WHERE latitude IS NOT NULL 
AND longitude IS NOT NULL;