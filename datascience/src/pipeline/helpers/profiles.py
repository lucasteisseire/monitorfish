import pandas as pd

from src.pipeline.helpers.segments import attribute_segments_to_catches
from src.pipeline.processing import df_to_dict_series


def compute_vessels_catch_profiles_by(catches: pd.DataFrame, by: str) -> pd.DataFrame:
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

    vessels_profiles = (
        catches_by[["cfr", by, "percentage"]]
        .groupby("cfr", observed=True)
        .apply(lambda df: df.set_index(by).to_dict()["percentage"])
        .rename(f"{by}_profile")
    )

    return vessels_profiles


def compute_vessels_segments_profiles(
    catches: pd.DataFrame,
    segments: pd.DataFrame,
    *,
    unassigned_catches_segment_label: str = "Aucun",
) -> pd.DataFrame:
    try:
        assert {"species", "gear", "fao_area", "weight"}.issubset(list(catches))
        assert {"segment", "species", "gear", "fao_area"}.issubset(list(segments))
    except AssertionError:
        raise ValueError(
            "catches and segments must include columns gear, fao_area and species."
        )

    total_catches = (
        catches.groupby("cfr", observed=True)["weight"]
        .sum()
        .rename("total_catch_weight")
    )

    segmented_catches = attribute_segments_to_catches(
        catches[catches.weight > 0],
        segments[["segment", "gear", "fao_area", "species"]],
        append_unassigned_catches=True,
        unassigned_catches_segment_label=unassigned_catches_segment_label,
    )

    catch_weights_per_segments = (
        segmented_catches.groupby(["cfr", "segment"], observed=True)[["weight"]]
        .sum()
        .reset_index()
    )

    catch_weights_per_segments = pd.merge(
        catch_weights_per_segments,
        total_catches,
        left_on="cfr",
        right_index=True,
    )

    catch_weights_per_segments["percentage"] = (
        catch_weights_per_segments["weight"]
        / catch_weights_per_segments["total_catch_weight"]
    )

    vessels_segments_profiles = (
        catch_weights_per_segments[["cfr", "segment", "percentage"]]
        .groupby("cfr", observed=True)
        .apply(lambda df: df.set_index("segment").to_dict()["percentage"])
        .rename("segment_profile")
    )

    vessels_segments_profiles = pd.merge(
        total_catches,
        vessels_segments_profiles,
        how="left",
        left_index=True,
        right_index=True,
    )

    return vessels_segments_profiles
