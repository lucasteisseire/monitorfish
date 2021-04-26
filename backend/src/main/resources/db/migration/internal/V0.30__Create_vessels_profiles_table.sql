CREATE TABLE public.vessels_profiles (
    cfr VARCHAR(12) PRIMARY KEY,
    length DOUBLE PRECISION,
    catch_weight_per_year DOUBLE PRECISION,
    trips_per_year INTEGER,
    typical_trip_catch_weight DOUBLE PRECISION,
    segment_profile JSONB,
    gear_profile JSONB,
    species_profile JSONB,
    fao_area_profile JSONB
);