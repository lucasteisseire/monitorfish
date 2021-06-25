import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Union

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.pipeline.processing import json_converter


@dataclass
class DatetimeChunk:
    """Class to represent a period of time between two dates, to support processing of
    time-series data in chunks.

    Dates are serialized, to allow processing by Prefect tasks.
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex, init=False)
    start_datetime_utc: datetime
    end_datetime_utc: datetime

    def __post_init__(self):
        self.start_datetime_utc = json_converter(self.start_datetime_utc)
        self.end_datetime_utc = json_converter(self.end_datetime_utc)


def get_first_day_of(d: datetime, of: str = "week") -> datetime:
    """Returns a datetime object representing the first day at midnight of the week or
    month of the input datetime.

    Args:
        d (datetime): datetime
        of (str): time unit of which to seek the first day. "week" or "month".
            Defaults to "week".

    Returns:
        datetime
    """

    if of == "week":
        day = d - timedelta(days=d.weekday())
        res = datetime(year=day.year, month=day.month, day=day.day)
    elif of == "month":
        res = datetime(year=d.year, month=d.month, day=1)
    else:
        raise ValueError(f"of must be 'week' or 'month', got '{of}'.")
    return res


def get_datetime_chunk(
    chunk_size: str = "week",
    chunks_from_now: int = 1,
    now: Union[datetime, None] = None,
) -> DatetimeChunk:
    """Returns a `DatetimeChunk` object with the following characteristics:
        - lasts one `chunk_size`
        - starts at midnight on the first day of the chunk `chunks_from_now` chunks from
        the current date, going back in time.

    For example, with chunk_size = 'week', chunks_from_now = 1, returns a `DatetimeChunk`
    object starting last week on Monday at 00:00 UTC and ending this week on Monday at
    00:00 UTC.

    Args:
        chunk_size (str, optional): 'month' or 'week'. Defaults to 'week'.
        chunks_from_now (int, optional): Number of chunks from current date to go back
            in time. Must be equal to or larger than 1. Defaults to 1.
        now (datetime): current datetime. If not supplied, the datetime of the server
            will be used.

    """
    try:
        assert isinstance(chunks_from_now, int) and chunks_from_now >= 1
    except AssertionError:
        e = f"`chunks_from_now` must be an integer >= 1, got {chunks_from_now}."
        raise ValueError(e)

    if chunk_size == "week":
        delta = relativedelta(weeks=1)
    elif chunk_size == "month":
        delta = relativedelta(months=1)
    else:
        raise ValueError(f"`chunk_size` must be 'week' or 'month', got '{chunk_size}'.")

    if now is None:
        now = datetime.utcnow()

    start_datetime_utc = get_first_day_of(now - chunks_from_now * delta, of=chunk_size)
    end_datetime_utc = start_datetime_utc + delta

    return DatetimeChunk(
        start_datetime_utc=start_datetime_utc, end_datetime_utc=end_datetime_utc
    )


def get_datetime_chunks(
    chunk_size: str = "week",
    chunks_from_now: int = 1,
    now: Union[datetime, None] = None,
) -> List[DatetimeChunk]:
    """Returns a list of `DatetimeChunk` objects, each having the following characteristics:
        - lasts one `chunk_size`
        - starts at midnight on the first day of a week or month (depending on the
            chunk_size argument)
    and collectively covering the period from `chunks_from_now` `chunk_size` from nown,
    going back in time.

    For example, with chunk_size = 'week', chunks_from_now = 3, returns a list of 3
    `DatetimeChunk` objects covering the last 3 full weeks, going back from now.

    Args:
        chunk_size (str, optional): 'month' or 'week'. Defaults to 'week'.
        chunks_from_now (int, optional): Number of chunks from current date to go back
            in time. Must be equal to or larger than 1. Defaults to 1.
        now (datetime): current datetime. If not supplied, the datetime of the server
            will be used.

    """
    try:
        assert chunk_size in ["week", "month"]
    except AssertionError:
        raise ValueError(f"`chunk_size` must be 'week' or 'month', got '{chunk_size}'.")

    try:
        assert isinstance(chunks_from_now, int) and chunks_from_now >= 1
    except AssertionError:
        e = f"`chunks_from_now` must be an integer >= 1, got {chunks_from_now}."
        raise ValueError(e)

    if now is None:
        now = datetime.utcnow()

    chunks = [
        get_datetime_chunk(chunk_size=chunk_size, chunks_from_now=i, now=now)
        for i in range(chunks_from_now, 0, -1)
    ]

    return chunks


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
        raise ValueError(f"how expects 'backward' or 'forward', got '{how}'")

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
            raise ValueError(f"unit must be None, 'h', 'min' or 's', got '{unit}'.")

    return intervals
