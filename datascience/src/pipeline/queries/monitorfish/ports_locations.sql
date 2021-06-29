SELECT 
    locode, 
    latitude, 
    longitude,
    stationary_vessels_h3_res9
FROM ports 
WHERE latitude IS NOT NULL 
AND longitude IS NOT NULL;