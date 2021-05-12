SELECT
    pt.locode,
    SDO_UTIL.TO_WKTGEOMETRY(shp.shape) geometry
FROM FMC2.FMC_ZONE_PORT_SHAPE shp
JOIN COMMUNFMC.C_CODE_PORT pt 
ON shp.idc_port = pt.idc_port
WHERE pt.locode IS NOT NULL