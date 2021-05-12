WITH recent_positions AS (
    SELECT DISTINCT internal_reference_number as vms_cfr
    FROM positions 
    WHERE date_time > CURRENT_TIMESTAMP - INTERVAL '7 days' 
    AND internal_reference_number IS NOT NULL
),

recent_ers AS (
    SELECT DISTINCT cfr as ers_cfr
    FROM ers
    WHERE operation_datetime_utc > CURRENT_TIMESTAMP - INTERVAL '7 days' 
    AND cfr IS NOT NULL
),

recent_vms_or_cfr AS (
    SELECT 
        COALESCE(vms_cfr, ers_cfr) AS cfr,
        CASE WHEN recent_positions.vms_cfr IS NOT NULL THEN TRUE ELSE FALSE END AS emitted_vms,
        CASE WHEN recent_ers.ers_cfr IS NOT NULL THEN TRUE ELSE FALSE END AS emitted_ers
    FROM recent_positions
    FULL OUTER JOIN recent_ers
    ON recent_positions.vms_cfr = recent_ers.ers_cfr
)

SELECT
    *
FROM recent_vms_or_cfr