from typing import Sequence, Tuple

import h3
import numpy as np
import pandas as pd
from pyproj import Geod
from sklearn.cluster import k_means

from src.pipeline.helpers.datetime import get_datetime_index_intervals


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
    df: pd.DataFrame,
    lat: str = "latitude",
    lon: str = "longitude",
    how: str = "backward",
    unit: str = "m",
):
    """Compute the distance between successive positions (rows). The DataFrame must
    have a datetime index, as well as latitude and longitude columns.
    Returns a Series with the same index as the input DataFrame and distances as
    values.


    Args:
        df

        lat (str): column name containing latitudes
        lon (str): column name containing longitudes
        how (str): if, 'forward', computes the interval between each position and the
            next one. if 'backward', computes the interval between each position and
            the previous one.
        unit (str): the distance unit (passed to h3.point_dist).

            Defaults to 'm'.

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

        if how == "forward":
            distances = np.append(distances, [np.nan])
        elif how == "backward":
            distances = np.append([np.nan], distances)
        else:
            raise ValueError(f"how must be 'forward' or 'backward', got f{how}")

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


def get_trip_numbers(
    positions: pd.DataFrame,
    is_at_port_column: str = "is_at_port",
    time_intervals_column: str = "time_interval",
    max_hours_within_trip: float = 4.0,
    min_number_positions_by_trip: int = 5,
) -> pd.Series:
    """Computes trip_numbers from positions of a vessel.
    Rows of the input DataFrame represent successive positions of the analyzed vessel.
    The DataFrame must have a datetime index and two columns indicating
        1) whether the position is at port
        2) the time interval between each position and the previous one

    From this, trips are computed and numbered, starting from 1 and increasing by steps
    of 1, based on the following rules:
        - Positions in a port do not belong to any trip and will received a null
        value, except the first position when a vessel enters a port and the last
        position before exiting a port
        - When the vessel leaves a port, a new trip starts and the trip number is
        incremented
        - When the interval between two successive positions is more than
        max_hours_within_trip occurs, a new trip starts and the trip number is
        incremented
        - Finally, all trips with less than min_number_positions_by_trip are deleted:
        the corresponding positions receive a null value

    Args:
        positions (pd.DataFrame) : DataFrame representing successive positions of a
            vessel
        is_at_port_column (str) : column name containing boolean values for whether a
            position is in a port or not
        time_intervals_column (str) : column name for the time interval (in hours)
            between each position and the next one (the next row)
        max_hours_within_trip (float) : maximum number of hours allowed between
            two successive positions of a trip
        min_number_positions_by_trip (int) : minimum number of positions per trip


    Returns:
        pd.Series: Series with the same index as the input and computed trip_number
            as values
    """
    if len(positions) < 2:
        trip_numbers = pd.Series(
            index=positions.index, data=[np.nan] * len(positions), name="trip_number"
        )
        return trip_numbers

    is_at_port = positions[is_at_port_column].values
    time_intervals = positions[time_intervals_column].values

    # Build couples of successive positions
    is_at_port_strides = np.lib.stride_tricks.sliding_window_view(
        is_at_port, window_shape=2, axis=0
    )

    # Compute port entries and exits based on changes of is_at_port status
    is_port_exit = (is_at_port_strides == (True, False)).all(axis=1)
    is_port_exit = np.append(is_port_exit, False)

    is_port_entry = (is_at_port_strides == (False, True)).all(axis=1)
    is_port_entry = np.append(False, is_port_entry)

    # Compute interruptions of signal for a certain time
    is_interrupted = time_intervals >= max_hours_within_trip

    is_at_sea = ~is_at_port
    is_in_trip = is_port_exit | is_at_sea | is_port_entry

    # A new trip starts when a vessel leaves a port, or upon signal interruption at sea
    is_new_trip = is_in_trip * (is_port_exit | is_interrupted)
    trip_numbers = is_new_trip.cumsum() + 1

    # null trip_numbers in ports
    trip_numbers = trip_numbers * is_in_trip
    trip_numbers = np.where(trip_numbers == 0, np.nan, trip_numbers)

    # Null trip_numbers with less than min_number_positions_by_trip
    unique_trip_numbers, positions_per_trip = np.unique(
        trip_numbers[~np.isnan(trip_numbers)], return_counts=True
    )

    invalid_trip_numbers = unique_trip_numbers[
        positions_per_trip < min_number_positions_by_trip
    ]

    trip_numbers = np.where(
        np.isin(trip_numbers, invalid_trip_numbers), np.nan, trip_numbers
    )

    # Build result Series
    trip_numbers = pd.Series(
        index=positions.index, data=trip_numbers, name="trip_number"
    )

    return trip_numbers


def enrich_positions(
    positions: pd.DataFrame,
    is_at_port: str = "is_at_port",
    lat: str = "latitude",
    lon: str = "longitude",
) -> pd.DataFrame:
    """Takes a pandas DataFrame with
        - a datetime index
        - latitude, longitude columns (float dtypes)
        - a is_at_port column (bool dtype)
    whose rows represent successive positions of a vessel

    Returns pandas DataFrame with the same index and columns, plus addtionnal computed
    features in new columns : speed, trip_numbers...

    Args:
        positions (pd.DataFrame): DataFrame representing a vessel route
        is_at_port (str): column name of bools
        lat (str) : column name of latitude values
        lon (str) : column name of longitude values

    Returns:
        pd.DataFrame: the same DataFrame, plus added columns with the computed features
    """
    #     course_changes = (
    #         get_course_changes(
    #             positions.course,
    #             positions.course.shift(-1).ffill()
    #         )
    #         .rename("course_change")
    #     )

    #     window_duration = 6
    #     window = f"{window_duration}h"

    #     window_course_changes = (
    #         course_changes
    #         .abs()
    #         .rolling(window)
    #         .sum()
    #         .rename("window_course_change")
    #     )

    enriched_positions = positions.copy(deep=True)

    enriched_positions["date"] = positions.index.date.astype(np.datetime64)

    enriched_positions["step_distance"] = get_step_distances(
        positions, how="backward"
    ).rename("step_distance")

    enriched_positions["time_interval"] = get_datetime_index_intervals(
        positions, unit="h", how="backward"
    ).rename("time_interval")

    enriched_positions["step_speed"] = (
        enriched_positions["step_distance"].values
        / 1852
        / enriched_positions["time_interval"].values
    )

    enriched_positions["trip_number"] = get_trip_numbers(
        enriched_positions[["is_at_port", "time_interval"]]
    )

    return enriched_positions


def find_fishing_transit_speed_threshold(
    speed_arr,
    init_fishing_speed=None,
    init_transit_speed=None,
    default_speed_threshold=4.5,
    min_points=200,
    min_cluster_separation=2.2,
):

    speed_arr = speed_arr[(speed_arr > 0) & (speed_arr < 15)]

    if init_fishing_speed is not None and init_transit_speed is not None:
        init = np.array([[init_fishing_speed], [init_transit_speed]])
        n_init = 1
    else:
        init = "k-means++"
        n_init = 10

    if len(speed_arr) < min_points:
        fishing_speed = None
        transit_speed = None
        fishing_std = None
        transit_std = None
        fishing_speed_threshold = default_speed_threshold
        cluster_separation = None

    else:
        (centroids, labels, _) = k_means(
            speed_arr[:, None], 2, init=init, n_init=n_init
        )

        speeds = centroids.flatten()
        fishing_speed, transit_speed = min(speeds), max(speeds)

        fishing_cluster_index = speeds.argmin()

        fishing_indices = labels.astype(bool)
        if fishing_cluster_index == 0:
            fishing_indices = ~fishing_indices

        fishing_std = speed_arr[fishing_indices].std()
        transit_std = speed_arr[~fishing_indices].std()

        cluster_separation = (transit_speed - fishing_speed) / (
            transit_std + fishing_std
        )
        if cluster_separation > min_cluster_separation:
            fishing_speed_threshold = (
                fishing_speed * transit_std + transit_speed * fishing_std
            ) / (fishing_std + transit_std)
        else:
            fishing_speed_threshold = default_speed_threshold

    counts, bins = np.histogram(
        speed_arr[(speed_arr > 0) & (speed_arr < 15)], bins=np.arange(0, 15, 0.5)
    )

    return (
        bins,
        counts,
        fishing_speed,
        fishing_std,
        transit_speed,
        transit_std,
        fishing_speed_threshold,
        cluster_separation,
    )


def get_trips(positions):

    #### TODO : move dropna to caller, use sort to reduce min max aggregations
    trips = positions.dropna(subset=["trip_number"])
    trips = trips.rename_axis(index=["date_time"])
    trips = trips.reset_index()
    trips = trips.groupby("trip_number")["date_time"]
    trips = trips.agg(["min", "max"])
    trips = trips.rename(
        columns={
            "min": "trip_start_datetime_utc",
            "max": "trip_end_datetime_utc",
        }
    )

    trips["trip_duration"] = (
        trips["trip_end_datetime_utc"] - trips["trip_start_datetime_utc"]
    )

    trip_distances = positions.dropna(subset=["trip_number"])
    trip_distances = trip_distances.groupby("trip_number")["step_distance"]
    trip_distances = trip_distances.sum()

    trips["trip_distance"] = trip_distances

    return trips


def analyze_vessel_route(
    positions: pd.DataFrame,
    days_analyzed: int,
    lat: str = "latitude",
    lon: str = "longitude",
) -> pd.Series:
    """Extracts information about a vessel's characteristics and habits from its
    historical positions.

    Positions of the vessel must be supplied in the form of a pandas DataFrame with a
    datetime index as well as latitude, longitude columns, whose rows, sorted by
    datetime, represent successive positions of a vessel over a period of time,
    possibly covering several months and several trips.

    In addition, a list of h3 indices of known ports must be supplied.

    The result is returned as a dictionnary of computed statistics and information.


    Args:
        positions (pd.DataFrame): DataFrame representing the vessel's positions
        ports_h3_ids (Sequence[str]): list-like object containing h3 indices of known
            ports
        days_analyzed (int): number of days of the analysis period. Used for
            normalization when covering less than a year.
        lat (str) : column name of latitude values
        lon (str) : column name of longitude values
        ports_h3_resolution (int): the h3 resolution in which ports indices are
            supplied

    Returns:
        pd.Series: Series of computed statistics
    """

    enriched_positions = enrich_positions(positions)

    days_emitted = enriched_positions["date"].nunique()
    emission_completeness_ratio = min(1, days_emitted / days_analyzed)

    # Compute trip metrics
    trips = get_trips(enriched_positions)
    number_trips = len(trips)
    trip_duration_median = trips.trip_duration.median()
    trip_distance_median = trips.trip_distance.median()
    trip_duration_sum = trips.trip_duration.sum()
    trip_distance_sum = trips.trip_distance.sum()

    # Estimate metrics on a full year
    estimated_annual_number_trips = int(number_trips * 365 / days_analyzed)
    estimated_annual_distance_travelled = trip_distance_sum * 365 / days_analyzed
    estimated_annual_time_at_sea = trip_duration_sum * 365 / days_analyzed

    #     (
    #         bins,
    #         counts,
    #         fishing_speed,
    #         fishing_std,
    #         transit_speed,
    #         transit_std,
    #         fishing_speed_threshold,
    #         cluster_separation,
    #     ) = find_fishing_transit_speed_threshold(
    #         enriched_positions[~enriched_positions.is_at_port].step_speed.values,
    #         init_fishing_speed=None,
    #         init_transit_speed=None,
    #     )

    return pd.Series(
        {
            "emission_completeness_ratio": emission_completeness_ratio,
            #             "fishing_speed": fishing_speed,
            #             "fishing_std": fishing_std,
            #             "transit_speed": transit_speed,
            #             "transit_std": transit_std,
            #             "fishing_speed_threshold": fishing_speed_threshold,
            #             "cluster_separation": cluster_separation,
            #             "speed_bins": bins,
            #             "speed_counts": counts,
            "estimated_annual_number_trips": estimated_annual_number_trips,
            "trip_duration_median": trip_duration_median,
            "trip_distance_median": trip_distance_median,
            "estimated_annual_time_at_sea": estimated_annual_time_at_sea,
            "estimated_annual_distance_travelled": estimated_annual_distance_travelled,
        }
    )
