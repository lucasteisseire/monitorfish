import pandas as pd


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
