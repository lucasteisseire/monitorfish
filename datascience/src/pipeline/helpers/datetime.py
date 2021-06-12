import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

import pandas as pd


@dataclass
class DatetimeChunk:
    """Class to represent a period of time between two dates, to support processing of
    time-series data in chunks"""

    id: str = field(default_factory=lambda: uuid.uuid4().hex, init=False)
    start_datetime_utc: datetime
    end_datetime_utc: datetime


def get_next_chunk_end_datetime(
    start_datetime_utc: datetime, max_datetime_utc: datetime, days_per_chunk: int
) -> datetime:
    """From a given datetime, computes the end datetime of the next chunk of some data
    to process, with the following rules:
        - the chunk starts at the indicated `start_datetime_utc`
        - the chunk lasts `days_per_chunk` days
        - if the end of the chunk exceeds `max_datetime_utc`, the chunk is clipped to
        `max_datetime_utc`, and is therefore shorted than `days_per_chunk` days

    Args:
        start_datetime_utc (datetime): Starting datetime.
        max_datetime_utc (datetime): The datetime that the chunk must not exceed.
        days_per_chunk (int): Number of days per chunk

    Returns:
        datetime: The next chunk end datetime
    """
    next_chunk_end_datetime = min(
        start_datetime_utc + timedelta(days=days_per_chunk),
        max_datetime_utc + timedelta(seconds=1),
    )

    return next_chunk_end_datetime


def get_datetime_chunks(
    start_datetime_utc: datetime, end_datetime_utc: datetime, days_per_chunk: int
) -> List[DatetimeChunk]:
    """Returns a list of `DatetimeChunk` objects between two dates with each chunk
    habing a duration as specified by the `days_per_chunk` argument.

    Args:
        start_datetime_utc (datetime): Start of analysis period
        end_datetime_utc (datetime): End of analysis period
        days_per_chunk (int): Number of days per chunk

    Returns:
        List[DatetimeChunk]: List of DatetimeChunk objects covering the specied period
    """
    res = []
    utcnow = datetime.utcnow()
    end_of_period_covered = start_datetime_utc

    while end_of_period_covered < end_datetime_utc:
        chunk_start = end_of_period_covered
        chunk_end = get_next_chunk_end_datetime(
            start_datetime_utc=chunk_start,
            max_datetime_utc=utcnow,
            days_per_chunk=days_per_chunk,
        )
        chunk = DatetimeChunk(
            start_datetime_utc=chunk_start, end_datetime_utc=chunk_end
        )
        res.append(chunk)
        end_of_period_covered = chunk_end

    return res


def get_datetime_index_intervals(
    df: pd.DataFrame, unit: str = None, how: str = "backward"
):
    """Takes a pandas DataFrame with a datetime index.
    Return a pandas Series with the same index and with time intervals between the
    successives index values as values.

    Args:
        df (pd.DataFrame): pandas DataFrame with datetime index
        unit (Union[str, None]):
            - if None, returns values as pandas Timedelta
            - if provided, must be one of 's', 'min' or 'h', in which case the result
            is returned as a float.

            Defaults to None.

        how (str): if, 'forward', computes the interval between each position and the
            next one. if 'backward', computes the interval between each position and
            the previous one.

            Defaults to 'backward'

    Returns:
        pd.Series: Series of time intervals between the index datetime labels
    """

    if how == "backward":
        shift = 1
    elif how == "forward":
        shift = -1
    else:
        raise ValueError(f"how expects 'backward' or 'forward', got {how}")

    intervals = pd.Series(
        index=df.index,
        data=shift
        * (df.index.values - df.reset_index().iloc[:, 0].shift(shift).values),
    )

    if unit:
        intervals = intervals.map(lambda dt: dt.total_seconds())
        if unit == "h":
            intervals = intervals / 3600
        elif unit == "min":
            intervals = intervals / 60
        elif unit == "s":
            pass
        else:
            raise ValueError(f"unit must be None, 'h', 'min' or 's', gpot {unit}.")

    return intervals
