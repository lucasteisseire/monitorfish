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
from src.pipeline.helpers.profiles import compute_vessels_catches_percentage_by
from src.pipeline.helpers.segments import attribute_segments_to_catches
from src.pipeline.processing import df_to_dict_series
from src.read_query import read_saved_query


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
def compute_profiles(catches: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:

    catches = catches.fillna({"weight": 0}).copy(deep=True)

    #     segmented_catches = (
    #         attribute_segments_to_catches(
    #             catches[["cfr", "ers_id", "gear", "fao_area", "species", "weight"]],
    #             segments[["segment", "gear", "fao_area", "species"]],
    #         )
    #         .groupby(["cfr", "segment"], observed=True)[["weight"]]
    #         .sum()
    #         .reset_index()
    #     )

    total_catches = (
        catches.groupby("cfr")["weight"].sum().rename("twelve_months_catch_weight")
    )
    catches_by_gear = compute_vessels_catches_percentage_by(catches, "gear")
    catches_by_species = compute_vessels_catches_percentage_by(catches, "species")
    catches_by_fao_area = compute_vessels_catches_percentage_by(catches, "fao_area")

    typical_catch_weight_by_trip = (
        catches.groupby(["cfr", "computed_trip_number"], observed=True)["weight"]
        .sum()
        .reset_index()
        .groupby("cfr")["weight"]
        .median()
    )

    number_of_trips = catches.groupby("cfr")["computed_trip_number"].nunique()

    res = pd.merge(total_catches, catches_by_gear, left_index=True, right_index=True)

    res = pd.merge(res, catches_by_species, left_index=True, right_index=True)

    res = pd.merge(res, catches_by_fao_area, left_index=True, right_index=True)

    res = pd.merge(res, typical_catch_weight_by_trip, left_index=True, right_index=True)

    res = pd.merge(res, number_of_trips, left_index=True, right_index=True)
    return res


# @task(checkpoint=False)
# def load_vessels_profiles(vessels_segments):  # pragma: no cover
#     logger = prefect.context.get("logger")
#     load(
#         vessels_segments,
#         table_name="current_segments",
#         schema="public",
#         db_name="monitorfish_remote",
#         logger=logger,
#         delete_before_insert=True,
#         pg_array_columns=["segments"],
#         handle_array_conversion_errors=True,
#         value_on_array_conversion_error="{}",
#         jsonb_columns=["gear_onboard", "species_onboard"],
#     )


with Flow("Updte vessels risk profile") as flow:

    catches = extract_catches()
    segments = extract_segments()
    segments = unnest(segments)
    vessels_profiles = compute_profiles(catches, segments)
#     current_segments = merge_segments_catches(catches, current_segments)
#     load_current_segments(current_segments)
