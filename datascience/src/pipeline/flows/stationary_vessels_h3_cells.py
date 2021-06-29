import os
import pickle

import h3
import numpy as np
import pandas as pd
import vptree
from prefect import Flow, Parameter, task
from sqlalchemy import text

from config import ROOT_DIRECTORY
from src.pipeline.generic_tasks import extract, load
from src.pipeline.helpers.spatial import get_h3_indices
from src.read_query import read_query


def get_distance_h3_point_dist(arr1, arr2):
    return h3.point_dist((arr1[0], arr1[1]), (arr2[0], arr2[1]))


class VPTree:
    """A Vantage-Point Tree to efficiently solve the nearest neighbor
    problem on (latitude, longitude) points.

    Args:
        ports (pd.DataFrame): DataFrame with 'latitude', 'longitude' and 'locode' columns

    Usage :

    >>> tree = VPTree(ports)
    >>> position = [50.23, -3.256]
    >>> tree.get_nearest_neighbor(position)

    """

    def __init__(self, ports: pd.DataFrame, id_column: str = "locode"):
        self.id_column = id_column
        self.tree = vptree.VPTree(
            ports[["latitude", "longitude", id_column]].values,
            get_distance_h3_point_dist,
        )

    def get_nearest_neighbor(self, lat: float, lon: float) -> dict:
        """Get the nearest neighbor of the input (latitude, longitude) point in the
        VP-tree.

        Args:
            lat (float) : latitude of point of which to search the nearest neighbor
            lon (float) : longitude of point of which to search the nearest neighbor
        """
        distance, nearest_neighbor = self.tree.get_nearest_neighbor([lat, lon])
        return {
            "nearest_latitude": nearest_neighbor[0],
            "nearest_longitude": nearest_neighbor[1],
            self.id_column: nearest_neighbor[2],
            "distance": distance,
        }


@task(checkpoint=False)
def get_zero_speed_positions():
    return extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/stationary_vessels_h3_cells.sql",
    )


@task(checkpoint=False)
def get_zero_speed_hexes(
    zero_speed_positions: pd.DataFrame,
    min_positions_by_hex: int = 100,
) -> pd.DataFrame:

    zero_speed_hexes = pd.DataFrame(
        get_h3_indices(zero_speed_positions, resolution=9), columns=["h3"]
    )

    zero_speed_hexes = (
        zero_speed_hexes.reset_index()
        .groupby("h3")[["index"]]
        .count()
        .rename(columns={"index": "count"})
    )

    zero_speed_hexes = zero_speed_hexes.reset_index()
    zero_speed_hexes = zero_speed_hexes[
        zero_speed_hexes["count"] > min_positions_by_hex
    ]
    zero_speed_hexes.index = np.arange(0, len(zero_speed_hexes))

    return zero_speed_hexes


@task(checkpoint=False)
def get_hex_centers(zero_speed_hexes: pd.DataFrame):
    zero_speed_hexes_centers = pd.DataFrame(
        zero_speed_hexes.apply(
            lambda row: list(h3.h3_to_geo(row["h3"])), axis=1
        ).values.tolist(),
        columns=pd.Index(["latitude", "longitude"]),
    )

    zero_speed_hexes = pd.concat([zero_speed_hexes, zero_speed_hexes_centers], axis=1)

    return zero_speed_hexes


@task(checkpoint=False)
def get_ports():
    query = """SELECT
        country_code_iso2,
        locode,
        port_name,
        is_fiching_port,
        is_landing_place,
        is_commercial_port,
        region,
        latitude,
        longitude
    FROM processed.ports"""

    ports = read_query("monitorfish_remote", query)
    return ports


@task(checkpoint=False)
def get_closest_ports(zero_speed_hexes, ports):
    ports_tree = VPTree(ports.dropna(subset=["latitude", "longitude"]))

    closest_ports = zero_speed_hexes.apply(
        lambda row: ports_tree.get_nearest_neighbor(row["latitude"], row["longitude"]),
        axis=1,
        result_type="expand",
    )

    closest_ports = closest_ports.rename(
        columns={
            "nearest_latitude": "nearest_port_latitude",
            "nearest_longitude": "nearest_port_longitude",
            "locode": "nearest_port_locode",
            "distance": "nearest_port_distance",
        }
    )

    zero_speed_hexes = pd.concat(
        [
            zero_speed_hexes,
            closest_ports,
        ],
        axis=1,
    )

    zero_speed_hexes = zero_speed_hexes[
        [
            "h3",
            "latitude",
            "longitude",
            "count",
            "nearest_port_locode",
            "nearest_port_distance",
            "nearest_port_latitude",
            "nearest_port_longitude",
        ]
    ].sort_values("count", ascending=False)

    return zero_speed_hexes


@task(checkpoint=False)
def get_unknown_port_stationary_vessels_h3_res9(zero_speed_hexes):
    return set(zero_speed_hexes.loc[zero_speed_hexes.nearest_port_distance >= 4, "h3"])


@task(checkpoint=False)
def load_unknown_port_stationary_vessels_h3_res9(
    unknown_port_stationary_vessels_h3_res9, path: str
):
    with open(ROOT_DIRECTORY / path, "wb") as f:
        pickle.dump(unknown_port_stationary_vessels_h3_res9, f)


@task(checkpoint=False)
def get_ports_h3_cells(ports, zero_speed_hexes):
    stationary_vessels_h3_res9 = (
        zero_speed_hexes[zero_speed_hexes.nearest_port_distance < 4]
        .groupby("nearest_port_locode")["h3"]
        .apply(list)
        .rename("stationary_vessels_h3_res9")
    )

    ports = pd.merge(
        ports,
        stationary_vessels_h3_res9,
        left_on="locode",
        right_index=True,
        how="left",
    )

    return ports


@task(checkpoint=False)
def load_ports(ports, ports_with_stationary_vessels_h3_res9_path):
    ports.to_csv(
        ROOT_DIRECTORY / ports_with_stationary_vessels_h3_res9_path, index=False
    )


with Flow("Stationary vessels h3 cells") as flow:
    unknown_port_stationary_vessels_h3_res9_path = Parameter(
        name="unknown_port_stationary_vessels_h3_res9_path",
        default="src/pipeline/data/unknown_port_stationary_vessels_h3_res9.pkl",
    )
    ports_with_stationary_vessels_h3_res9_path = Parameter(
        name="ports_with_stationary_vessels_h3_res9_path",
        default="data/pipeline/ports/ports.csv",
    )

    ports = get_ports()
    zero_speed_positions = get_zero_speed_positions()
    zero_speed_hexes = get_zero_speed_hexes(zero_speed_positions)
    zero_speed_hexes = get_hex_centers(zero_speed_hexes)
    zero_speed_hexes = get_closest_ports(zero_speed_hexes, ports)

    unknown_port_stationary_vessels_h3_res9 = (
        get_unknown_port_stationary_vessels_h3_res9(zero_speed_hexes)
    )

    load_unknown_port_stationary_vessels_h3_res9(
        unknown_port_stationary_vessels_h3_res9,
        unknown_port_stationary_vessels_h3_res9_path,
    )

    ports = get_ports_h3_cells(ports, zero_speed_hexes)
    load_ports(ports, ports_with_stationary_vessels_h3_res9_path)
