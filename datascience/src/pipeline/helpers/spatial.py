from typing import Tuple

import h3
import numpy as np
import pandas as pd
from pyproj import Geod


def estimate_current_position(
    last_latitude: float,
    last_longitude: float,
    course: float,
    speed: float,
    time_since_last_position: float,
    max_time_since_last_position: float = 2,
    on_error: str = "ignore",
) -> Tuple[float, float]:
    """Estimate the current position of a vessel based on its last position, course and
    speed. If the last position is older than max_time_since_last_position, returns
    None.

    Args:
        last_latitude (float): last known latitude of vessel
        last_longitude (float): last known longitude of vessel
        course (float): last known route of vessel in degrees
        speed (float): last known speed of vessel in nots
        time_since_last_position (float): time since last known position of vessel, in hours
        max_time_since_last_position (float): maximum time in hours since last position,
            after which the estimation is not performed (returns None instead).
            Defaults to 2.
        on_error (str): 'ignore' or 'raise'.

    Returns:
        float: estimated current latitude
        float: estimated current longitude
    """
    geod = Geod(ellps="WGS84")
    if time_since_last_position > 2:
        lat, lon = None, None
    else:
        try:
            distance = speed * time_since_last_position * 1852
            lon, lat, _ = geod.fwd(last_longitude, last_latitude, course, distance)
        except:
            if on_error == "ignore":
                lat, lon = None, None
            else:
                raise
    return lat, lon


def get_step_distances(
    df: pd.DataFrame, lat="latitude", lon="longitude", nan_position="last", unit="m"
):
    """Compute the distance between successive positions (rows) The DataFrame must have
    a datetime index and latitude and longitude columns.
    Returns a Series with the same index as the input DataFrame and distances as
    values.
    """

    if len(df) < 2:
        distances = [np.nan] * len(df)
    else:

        strides = np.lib.stride_tricks.sliding_window_view(
            df[[lat, lon]].values, 2, axis=0
        ).reshape((len(df) - 1, 4))

        distances = np.apply_along_axis(
            lambda x: h3.point_dist(tuple(x[[0, 2]]), tuple(x[[1, 3]]), unit=unit),
            axis=1,
            arr=strides,
        )

        if nan_position == "last":
            distances = np.append(distances, [np.nan])
        elif nan_position == "first":
            distances = np.append([np.nan], distances)
        else:
            raise ValueError(
                f"nan_position must be 'first' or 'last', got f{nan_position}"
            )

    res = pd.Series(index=df.index, name="distance", data=distances)

    return res


def get_h3_indices(
    df: pd.DataFrame,
    lat: float = "latitude",
    lon: float = "longitude",
    resolution: int = 12,
):

    res = df.apply(
        lambda row: h3.geo_to_h3(row["latitude"], row["longitude"], resolution), axis=1
    )
    return res
