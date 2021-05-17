###################################### Activity ######################################
# Nb marées : nb de DEP / RTP ou analyse VMS
# Durée typique de marée : nb de FAR / marée ou écart typique DEP - RTP ou en analyse VMS
# Volume captures par an /!\ outliers avec facteur 1000 sur le poids de capture
# Volume de captures rapporté à la taille du navire
# Volume captures / marée (prendre la médiane plutôt que la moyenne pour éviter outliers)
# Segments de flotte : % de captures par segment - en kg et / ou en nb de FAR
# Top espèces
# Top engins
# Top areas
# Km parcourus

###################################### Controls ######################################
# Nb de contrôles moyen par an
# Nb de contrôles moyen par an rapporté à l'activité du navire (en jours de mer, en marées, en kg pêchés, en nb de messages FAR... ?)
# Taux d'infraction


#################################### Risk factors ####################################
# Suspicion (analyse parcours VMS) activité de pêche non déclarée
# Jours en mer sans FAR
# Ecarts FAR / LAN

from typing import Union

import pandas as pd
import prefect
from prefect import Flow, task

from src.pipeline.generic_tasks import extract, load
from src.pipeline.helpers.profiles import (
    compute_vessels_catch_profiles_by,
    compute_vessels_segments_profiles,
)
from src.pipeline.processing import df_to_dict_series
from src.read_query import read_saved_query


@task(checkpoint=False)
def extract_all_recent_positions(within: str = "1 month"):
    positions = extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/all_positions.sql",
        dtypes={"cfr": "category"},
        params={"within": within},
    )
    positions = positions.set_index("date_time")
    return positions


@task(checkpoint=False)
def extract_lengths():
    return extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/vessel_lengths.sql",
    )


@task(checkpoint=False)
def extract_trips():
    return extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/twelve_months_trips.sql",
    )


@task(checkpoint=False)
def extract_catches():
    return extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/twelve_months_catches.sql",
        dtypes={
            "ers_id": "category",
            "cfr": "category",
            "gear": "category",
            "species": "category",
            "fao_area": "category",
            "computed_trip_number": "category",
        },
    )


@task(checkpoint=False)
def extract_segments():
    return extract(
        db_name="monitorfish_remote", query_filepath="monitorfish/fleet_segments.sql"
    )


@task(checkpoint=False)
def unnest(segments: pd.DataFrame) -> pd.DataFrame:
    return (
        segments.explode("gears")
        .explode("fao_areas")
        .explode("species")
        .rename(columns={"fao_areas": "fao_area", "gears": "gear"})
    )


@task(checkpoint=False)
def compute_profiles(
    catches: pd.DataFrame,
    segments: pd.DataFrame,
    lengths: pd.DataFrame,
    trips: pd.DataFrame,
) -> pd.DataFrame:

    logger = prefect.context.get("logger")

    catches = catches.fillna({"weight": 0}).copy(deep=True)

    catch_columns = [
        "cfr",
        "computed_trip_number",
        "ers_id",
        "gear",
        "fao_area",
        "species",
        "weight",
    ]
    catches = catches[catch_columns]

    logger.info("Compute vessels' catch profiles by gear, by species and by fao area.")
    catches_by_gear = compute_vessels_catch_profiles_by(catches, "gear")
    catches_by_species = compute_vessels_catch_profiles_by(catches, "species")
    catches_by_fao_area = compute_vessels_catch_profiles_by(catches, "fao_area")

    logger.info("Compute vessels' typical (median) catch weight per trip.")
    typical_catch_weight_by_trip = (
        catches.groupby(["cfr", "computed_trip_number"], observed=True)["weight"]
        .sum()
        .reset_index()
        .groupby("cfr", observed=True)["weight"]
        .median()
        .rename("typical_trip_catch_weight")
    )

    logger.info("Compute vessels' catch profiles by fleet segment.")
    vessels_segments_profiles = compute_vessels_segments_profiles(
        catches,
        segments,
        unassigned_catches_segment_label="Aucun",
    ).rename(columns={"total_catch_weight": "catch_weight_per_year"})

    logger.info("Merge all profiles.")
    vessels_profiles = pd.merge(
        vessels_segments_profiles,
        catches_by_gear,
        left_index=True,
        right_index=True,
        how="outer",
    )

    vessels_profiles = pd.merge(
        vessels_profiles,
        catches_by_species,
        left_index=True,
        right_index=True,
        how="outer",
    )

    vessels_profiles = pd.merge(
        vessels_profiles,
        catches_by_fao_area,
        left_index=True,
        right_index=True,
        how="outer",
    )

    vessels_profiles = pd.merge(
        vessels_profiles,
        typical_catch_weight_by_trip,
        left_index=True,
        right_index=True,
        how="outer",
    )

    vessels_profiles = pd.merge(
        vessels_profiles,
        trips.set_index("cfr"),
        left_index=True,
        right_index=True,
        how="outer",
    )

    vessels_profiles = pd.merge(
        vessels_profiles,
        lengths.set_index("cfr"),
        left_index=True,
        right_index=True,
        how="left",
    )

    return vessels_profiles.reset_index()


@task(checkpoint=False)
def load_vessels_profiles(vessels_profiles):

    load(
        vessels_profiles,
        table_name="vessels_profiles",
        schema="public",
        db_name="monitorfish_remote",
        logger=prefect.context.get("logger"),
        delete_before_insert=True,
        jsonb_columns=[
            "segment_profile",
            "gear_profile",
            "species_profile",
            "fao_area_profile",
        ],
    )


with Flow("Update vessels profiles") as flow:

    catches = extract_catches()
    lengths = extract_lengths()
    trips = extract_trips()
    segments = extract_segments()
    segments = unnest(segments)
    vessels_profiles = compute_profiles(catches, segments, lengths, trips)
    load_vessels_profiles(vessels_profiles)
