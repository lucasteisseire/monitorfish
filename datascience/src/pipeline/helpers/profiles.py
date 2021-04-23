import pandas as pd

from src.pipeline.processing import df_to_dict_series


def compute_vessels_catches_percentage_by(
    catches: pd.DataFrame, by: str
) -> pd.DataFrame:
    """For each vessel (identified by its `cfr`), computes the percentage of catch
    weight made with each `by`.

    Arguments:
        catches (pd.DataFrame): DataFrame of catches, must have the following columns:
            - cfr
            - weight
            - the column referenced by `by`
        by (str): column name on which to perform percentage calculations

    Returns:
        pd.DataFrame
    """
    total_catches = catches.groupby("cfr")["weight"].sum().rename("total_weight")

    catches_by = (
        catches.groupby(["cfr", by], observed=True)[  # required for categorical data
            "weight"
        ]
        .sum()
        .reset_index()
    )

    catches_by = pd.merge(catches_by, total_catches, on="cfr")
    catches_by["percentage"] = catches_by["weight"] / catches_by["total_weight"]

    catches_by[f"{by}_profile"] = df_to_dict_series(catches_by[[by, "percentage"]])
    vessels_profiles = catches_by.groupby("cfr")[f"{by}_profile"].apply(list)
    return vessels_profiles
