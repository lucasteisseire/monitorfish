-- The trip_number attribute is not used as it is only available for french vessels
-- A computed trip_number is made by counting DEP messages, LAN messages and 
WITH deps AS (
    SELECT
        cfr,
        COUNT(operation_number) as number_deps
    FROM public.ers
    WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
    AND operation_type = 'DAT'
    AND log_type = 'DEP'
    GROUP BY cfr
),

lans AS (
    SELECT
        cfr,
        COUNT(operation_number) as number_lans
    FROM public.ers
    WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
    AND operation_type = 'DAT'
    AND log_type = 'LAN'
    GROUP BY cfr
),

trip_numbers AS (
    SELECT
        cfr,
        COUNT(DISTINCT trip_number) as number_trips
    FROM public.ers
    WHERE operation_datetime_utc >= CURRENT_TIMESTAMP - INTERVAL '1 year'
    AND operation_type = 'DAT'
    GROUP BY cfr
),
    
t1 AS (SELECT 
        COALESCE(deps.cfr, lans.cfr) AS cfr,
        number_deps,
        number_lans
    FROM deps
    FULL OUTER JOIN lans
    ON deps.cfr = lans.cfr
)

SELECT
    COALESCE(t1.cfr, trip_numbers.cfr) AS cfr,
    GREATEST(number_deps, number_lans, number_trips) AS trips_per_year
FROM t1
FULL OUTER JOIN trip_numbers
ON t1.cfr = trip_numbers.cfr