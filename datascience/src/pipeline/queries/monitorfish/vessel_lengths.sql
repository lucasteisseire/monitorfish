SELECT
    cfr,
    length,
    flag_state
FROM public.vessels
WHERE cfr IS NOT NULL