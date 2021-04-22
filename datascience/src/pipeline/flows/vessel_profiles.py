###################################### Activity ######################################
# Nb marées : nb de DEP / RTP ou analyse VMS
# Durée typique de marée : nb de FAR / marée ou écart typique DEP - RTP ou en analyse VMS
# Volume captures par an /!\ outliers avec facteur 1000 sur le poids de capture
# Volume de captures rapporté à la taille du navire
# Volume captures / marée (prendre la médiane plutôt que la moyenne pour éviter outliers)
# Segments de flotte : % de captures par segment - en kg et / ou en nb de FAR
# Top espèces
# Top engins
# Top zones
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
from src.pipeline.helpers.segments import catch_zone_isin_fao_zone
from src.pipeline.processing import df_to_dict_series
from src.read_query import read_saved_query


@task(checkpoint=False)
def extract_catches():
    return extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/twelve_months_catches.sql",
        #         dtypes={
        #             "ers_id": "category",
        #             "cfr": "category",
        #             "gear": "category",
        #             "species": "category",
        #             "fao_zone": "category",
        #         }
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
        .explode("fao_zones")
        .explode("species")
        .rename(columns={"fao_zones": "fao_zone", "gears": "gear"})
    )


@task(checkpoint=False)
def compute_segments(catches: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:

    catches_ = catches[["cfr", "ers_id", "gear", "fao_zone", "species", "weight"]]
    segments_ = segments[["segment", "gear", "fao_zone", "species"]]

    # Merge catches and segments on gear and species
    segments_gear_species = pd.merge(
        segments_,
        catches_,
        on=["species", "gear"],
        suffixes=("_of_segment", "_of_catch"),
    )

    # Merge catches and segments only on gear, for segments without a species criterion
    segments_gear_only_ = segments_[segments_.species.isna()].drop(columns=["species"])

    segments_gear_only = pd.merge(
        segments_gear_only_, catches_, on="gear", suffixes=("_of_segment", "_of_catch")
    )

    # Merge catches and segments only on species, for segments without a gear criterion
    segments_species_only_ = segments_[segments_.gear.isna()].drop(columns=["gear"])

    segments_species_only = pd.merge(
        segments_species_only_,
        catches_,
        on="species",
        suffixes=("_of_segment", "_of_catch"),
    )

    # Match catches to all segments that have no criterion on species nor on gears
    segments_no_gear_no_species_ = segments_[
        segments_[["gear", "species"]].isna().all(axis=1)
    ][["segment", "fao_zone"]]

    segments_no_gear_no_species = pd.merge(
        segments_no_gear_no_species_,
        catches_,
        how="cross",
        suffixes=("_of_segment", "_of_catch"),
    )

    # Concatenate the 4 sets of matched (catches, segments)
    segments_ = pd.concat(
        [
            segments_gear_species,
            segments_gear_only,
            segments_species_only,
            segments_no_gear_no_species,
        ]
    )

    # Matched (catches, segments) now need to be filtered to keep only the matches
    # that satisfy the fao_zone criterion. A catch made in '27.7.b' will satisfy
    # the fao criterion of a segment whose fao_zone is '27.7', so we check that the
    # fao zone of the segment is a substring of the fao zone of the catch.
    segments_ = segments_[
        (
            segments_.apply(
                lambda row: catch_zone_isin_fao_zone(
                    row.fao_zone_of_catch, row.fao_zone_of_segment
                ),
                axis=1,
            )
        )
    ]

    # Finally, aggregate by vessel and by segment
    segments_ = (
        segments_.groupby(["cfr", "segment"], observed=True)[["weight"]]
        .sum()
        .reset_index()
    )

    #     total_catches_by_vessel = catches.groupby("cfr")["weight"].sum()

    #     segments_

    return segments_


@task(checkpoint=False)
def load_vessels_profiles(vessels_segments):  # pragma: no cover
    logger = prefect.context.get("logger")
    load(
        vessels_segments,
        table_name="current_segments",
        schema="public",
        db_name="monitorfish_remote",
        logger=logger,
        delete_before_insert=True,
        pg_array_columns=["segments"],
        handle_array_conversion_errors=True,
        value_on_array_conversion_error="{}",
        jsonb_columns=["gear_onboard", "species_onboard"],
    )


# with Flow(
#     "Extract the last DEP of each vessel in the `ers` table, "
#     "load into the `current_segments` table"
# ) as flow:

#     catches = extract_catches()
#     segments = extract_segments()
#     segments = unnest(segments)
#     current_segments = compute_segments(catches, segments)
#     current_segments = merge_segments_catches(catches, current_segments)
#     load_current_segments(current_segments)
