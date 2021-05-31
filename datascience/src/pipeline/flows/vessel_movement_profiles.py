from typing import Union

import numpy as np
import pandas as pd
import prefect
from prefect import Flow, task

from src.pipeline.generic_tasks import extract, load
from src.pipeline.helpers.ports import get_ports_h3_set
from src.pipeline.helpers.spatial import analyze_vessel_route, get_h3_indices
from src.read_query import read_saved_query


# @task(checkpoint=False)
def extract_all_positions(start: str = "3 months", end: str = "0 days"):
    positions = extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/all_positions.sql",
        dtypes={
            "cfr": "category",
            "external_immatriculation": "category",
            "ircs": "category",
        },
        params={"start": start, "end": end},
    )
    positions = positions.set_index("date_time")
    return positions


# @task(checkpoint=False)
def tag_positions_at_port(positions):

    positions = positions.copy(deep=True)

    h3_indices = get_h3_indices(
        positions, lat="latitude", lon="longitude", resolution=7
    ).rename("h3")

    ports_h3_ids = get_ports_h3_set(resolution=7, k_ring=1)

    positions["is_at_port"] = np.isin(h3_indices.values, ports_h3_ids)

    return positions


# @task(checkpoint=False)
def compute_vessel_movement_profiles(positions, ports_h3_ids):
    return positions.groupby("cfr", observed=True).apply(
        lambda x: analyze_vessel_route(x, ports_h3_ids, 1)
    )


@task(checkpoint=False)
def load_vessel_movement_profiles(profiles):

    load(
        profiles,
        table_name="vessel_movement_profiles",
        schema="public",
        db_name="monitorfish_remote",
        logger=prefect.context.get("logger"),
        delete_before_insert=True,
    )


# def wip_flow():
#     positions = extract_all_recent_positions("3 months")
#     positions = tag_positions_at_port(positions)
#     profiles = positions.groupby("cfr", observed=True).apply(
#         lambda x: analyze_vessel_route(x, days_analyzed=1)
#     )
#     return profiles


# with Flow("Vessel movement profiles") as flow:
#     pass
