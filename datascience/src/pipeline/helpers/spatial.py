from dataclasses import dataclass
from typing import Iterable, Set, Tuple, Union

import h3
import pandas as pd
from pyproj import Geod
from shapely.geometry import MultiPolygon, Polygon


@dataclass
class Position:
    latitude: float
    longitude: float


def to_multipolygon(p: Union[Polygon, MultiPolygon]) -> MultiPolygon:
    """
    Returns a MultiPolygon of the input Polygon or MultiPolygon geometry.
    """

    if isinstance(p, Polygon):
        res = MultiPolygon([p])
    elif isinstance(p, MultiPolygon):
        res = p
    else:
        raise ValueError("Input must be shapely Polygon or MultiPolygon")

    return res


def estimate_current_position(
    last_latitude: float,
    last_longitude: float,
    course: float,
    speed: float,
    hours_since_last_position: float,
    max_hours_since_last_position: float = 2.0,
    on_error: str = "ignore",
) -> Tuple[float, float]:
    """Estimate the current position of a vessel based on its last position, course and
    speed. If the last position is older than max_hours_since_last_position, or is in
    the future (i.e. hours_since_last_position is negative), returns None.

    Args:
        last_latitude (float): last known latitude of vessel
        last_longitude (float): last known longitude of vessel
        course (float): last known route of vessel in degrees
        speed (float): last known speed of vessel in nots
        hours_since_last_position (float): time since last known position of vessel, in hours
        max_hours_since_last_position (float): maximum time in hours since last position,
            after which the estimation is not performed (returns None instead).
            Defaults to 2.0.
        on_error (str): 'ignore' or 'raise'.

    Returns:
        float: estimated current latitude
        float: estimated current longitude
    """
    if not 0 <= hours_since_last_position <= max_hours_since_last_position:
        lat, lon = None, None
    else:
        geod = Geod(ellps="WGS84")
        try:
            distance = speed * hours_since_last_position * 1852
            lon, lat, _ = geod.fwd(last_longitude, last_latitude, course, distance)
        except:
            if on_error == "ignore":
                lat, lon = None, None
            elif on_error == "raise":
                raise
            else:
                raise ValueError(
                    f"on_error argument must be 'ignore' or 'raise', got {on_error}."
                )
    return lat, lon


def get_h3_indices(
    df: pd.DataFrame,
    lat: str = "latitude",
    lon: str = "longitude",
    resolution: int = 12,
) -> pd.Series:
    """
    Returns a Series with the same index as the input DataFrame and values equal to the
    h3 index corresponding to the latitude and longitude of the indicated columns of
    the DataFrame

    Args:
        df (pd.DataFrame): DataFrame with latitude and longitude coordinates in 2 of
          its columns
        lat (str): name of the column containing latitudes. Defaults to "latitude".
        lon (str): name of the column containing longitudes. Defaults to "longitude".
        resolution (int): h3 resolution of the h3 cells to output.

    Returns:
        pd.Series: h3 cells indices
    """

    if len(df) == 0:
        res = pd.Series([], dtype=object)
    else:
        res = df.apply(
            lambda row: h3.geo_to_h3(row["latitude"], row["longitude"], resolution),
            axis=1,
        )

    return res


def get_k_ring_of_h3_cells(h3_sequence: Iterable[str], k: int) -> Set[str]:
    """
    Takes an list-like sequence of h3 cells and an integer k, returns the set of h3
    cells that belong to the k-ring of at least one of the h3 cells in the input
    sequence.

    Args:
        h3_sequence (sequence): sequence of h3 cells
        k (int): number of rings to add around the input cells

    Returns:
        sequence[str]: sequence of h3 cells belonging to the k-ring of at least one of
            the h3 cells in the input sequence
    """
    h3_cells = [h3.k_ring(h, k) for h in h3_sequence]
    return set.union(*h3_cells)


def point_dist(position1: Position, position2: Position) -> float:
    """
    Computes the spherical distance between two Position objects in
    meters.

    Args:
        position1 (Position)
        position2 (Position)

    Returns:
        float: distance in meters between the two input Positions
    """

    d = h3.point_dist(
        (position1.latitude, position1.longitude),
        (position2.latitude, position2.longitude),
        unit="m",
    )

    return d
