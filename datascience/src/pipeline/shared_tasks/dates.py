from datetime import datetime, timedelta
from typing import List, Union

from prefect import task

from src.pipeline.helpers import dates


@task(checkpoint=False)
def make_periods(
    start_datetime_utc: datetime,
    end_datetime_utc: datetime,
    period_duration: timedelta,
    overlap: Union[None, timedelta] = None,
) -> List[dates.Period]:
    """
    `Task` version of the function `src.pipeline.helpers.dates.make_periods`.

    `src.pipeline.helpers.dates.make_periods` is recursive, hence the construction as a
    python function first and not directly as Prefect `Task`.

    See `src.pipeline.helpers.dates.make_periods` for help.
    """
    return dates.make_periods(
        start_datetime_utc=start_datetime_utc,
        end_datetime_utc=end_datetime_utc,
        period_duration=period_duration,
        overlap=overlap,
    )
