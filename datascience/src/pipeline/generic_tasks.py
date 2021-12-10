import logging
from pathlib import Path
from typing import List, Union

import geopandas as gpd
import pandas as pd
import prefect
from prefect import task

from src.db_config import create_engine
from src.pipeline import utils
from src.pipeline.processing import (
    df_values_to_psql_arrays,
    prepare_df_for_loading,
    to_json,
)
from src.pipeline.utils import get_table, make_create_temp_table_query, psql_insert_copy
from src.read_query import read_saved_query


def extract(
    db_name: str,
    query_filepath: Union[Path, str],
    dtypes: Union[None, dict] = None,
    parse_dates: Union[list, dict, None] = None,
    params=None,
    backend: str = "pandas",
    geom_col: str = "geom",
    crs: Union[int, None] = None,
) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
    """Run SQL query against the indicated database and return the result as a
    `pandas.DataFrame`.

    Args:
        db_name (str): name of the database to extract from : "fmc", "ocan",
            "monitorfish_local" or "monitorfish_remote"
        query_filepath (Union[Path, str]): path to .sql file, starting from the saved
            queries folder. example : "ocan/nav_fr_peche.sql"
        dtypes (Union[None, dict], optional): If specified, use {col: dtype, …}, where
            col is a column label and dtype is a numpy.dtype or Python type to cast
            one or more of the DataFrame’s columns to column-specific types.
            Defaults to None.
        parse_dates (Union[list, dict, None], optional):
            - List of column names to parse as dates.
            - Dict of ``{column_name: format string}`` where format string is
            strftime compatible in case of parsing string times or is one of
            (D, s, ns, ms, us) in case of parsing integer timestamps.
            - Dict of ``{column_name: arg dict}``, where the arg dict corresponds
            to the keyword arguments of :func:`pandas.to_datetime`

            Defaults to None.
        params (Union[dict, None], optional): Parameters to pass to execute method.
            Defaults to None.
        backend (str, optional) : 'pandas' to run a SQL query and return a
            `pandas.DataFrame` or 'geopandas' to run a PostGIS query and return a
            `geopandas.GeoDataFrame`. Defaults to 'pandas'.
        geom_col (str, optional): column name to convert to shapely geometries when
            `backend` is 'geopandas'. Ignored when `backend` is 'pandas'. Defaults to
            'geom'.
        crs (Union[None, str], optional) : CRS to use for the returned GeoDataFrame;
            if not set, tries to determine CRS from the SRID associated with the first
            geometry in the database, and assigns that to all geometries. Ignored when
            `backend` is 'pandas'. Defaults to None.

    Returns:
        Union[pd.DataFrame, gpd.GeoDataFrame]: Query results
    """

    res = read_saved_query(
        db_name,
        query_filepath,
        parse_dates=parse_dates,
        params=params,
        backend=backend,
        geom_col=geom_col,
        crs=crs,
    )

    if dtypes:
        res = res.astype(dtypes)

    return res


def load(
    df: Union[pd.DataFrame, gpd.GeoDataFrame],
    table_name: str,
    schema: str,
    db_name: str,
    logger: logging.Logger,
    how: str = "replace",
    pg_array_columns: Union[None, list] = None,
    handle_array_conversion_errors: bool = True,
    value_on_array_conversion_error="{}",
    jsonb_columns: Union[None, list] = None,
    table_id_column: Union[None, str] = None,
    df_id_column: Union[None, str] = None,
    nullable_integer_columns: Union[None, list] = None,
    timedelta_columns: Union[None, list] = None,
):
    """
    Load a DataFrame or GeoDataFrame to a database table using sqlalchemy. The table
    must already exist in the database.

    Args:
        df (Union[pd.DataFrame, gpd.GeoDataFrame]): data to load
        table_name (str): name of the table
        schema (str): database schema of the table
        db_name (str): 'monitorfish_remote' or 'monitorfish_local'
        logger (logging.Logger): logger instance,
        how (str): one of
          - 'replace' to delete all rows in the table before loading
          - 'append' to append the data to rows already in the table
          - 'upsert' to append the rows to the table, replacing the rows whose id is
            already
        pg_array_columns (Union[None, list]): columns containing sequences that must be
          serialized before loading into columns with Postgresql `Array` type
        handle_array_conversion_errors (bool): whether to handle or raise upon error
          during the serialization of columns to load into Postgresql `Array` columns
        value_on_array_conversion_error: if `handle_array_conversion_errors`, the value
          to use when an error must be handled
        jsonb_columns (Union[None, list]): columns containing values that must be
          serialized before loading into columns with Postgresql `JSONB` type
        table_id_column (Union[None, str]): name of the table column to use an id.
          Required if `how` is "upsert".
        df_id_column (Union[None, str]): name of the DataFrame column to use an id.
          Required if `how` is "upsert".
        nullable_integer_columns (Union[None, list]): columns containing values
          that must loaded into columns with Postgresql `Integer` type. If these
          columns contain `NA` values, pandas will automatically change the dtype to
          `float` and the loading into Postgreql `Integer` columns will fail, so it is
          necessary to serialize these values as `Integer`-compatible `str` objects.
        timedelta_columns (Union[None, list]): columns containing `Timedelta` values to
          load into Postgresql `Interval` columns. If these columns contain `NaT`
          values, the loading will fail, so it is necessary to serialize these values
          as `Interval`-compatible `str` objects.
    """

    df_ = prepare_df_for_loading(
        df,
        logger,
        pg_array_columns=pg_array_columns,
        handle_array_conversion_errors=handle_array_conversion_errors,
        value_on_array_conversion_error=value_on_array_conversion_error,
        jsonb_columns=jsonb_columns,
        nullable_integer_columns=nullable_integer_columns,
        timedelta_columns=timedelta_columns,
    )

    e = create_engine(db_name)
    table = get_table(table_name, schema, e, logger)

    with e.begin() as connection:

        if how == "replace":
            # Delete all rows from table
            utils.delete(table, connection, logger)

        elif how == "upsert":
            # Delete rows that are in the DataFrame from the table

            try:
                assert df_id_column is not None
            except AssertionError:
                raise ValueError("df_id_column cannot be null if how='upsert'")
            try:
                assert table_id_column is not None
            except AssertionError:
                raise ValueError("table_id_column cannot be null if how='upsert'")

            ids_to_delete = set(df[df_id_column].unique())

            utils.delete_rows(
                table=table,
                id_column=table_id_column,
                ids_to_delete=ids_to_delete,
                connection=connection,
                logger=logger,
            )

        elif how == "append":
            # Nothing to do
            pass

        else:
            raise ValueError(f"how must be 'replace', 'upsert' or 'append', got {how}")

        # Insert data into table
        logger.info(f"Loading into {schema}.{table_name}")

        if isinstance(df_, gpd.GeoDataFrame):
            logger.info("GeodateFrame detected, using to_postgis")
            df_.to_postgis(
                name=table_name,
                con=connection,
                schema=schema,
                index=False,
                if_exists="append",
            )

        elif isinstance(df_, pd.DataFrame):
            df_.to_sql(
                name=table_name,
                con=connection,
                schema=schema,
                index=False,
                method=psql_insert_copy,
                if_exists="append",
            )

        else:
            raise ValueError("df must be DataFrame or GeoDataFrame.")


def delete_rows(
    *,
    table_name: str,
    schema: str,
    db_name: str,
    table_id_column: str,
    ids_to_delete: set,
    logger: logging.Logger,
):
    """
    Delete rows from a database table.

    Args:
        table_name (str): name of the table
        schema (str): database schema of the table
        db_name (str): name of the database. One of
          - 'monitorfish_remote'
          - 'monitorfish_local'
        table_id_column (str): name of the id column in the database.
        ids_to_delete (set): the ids of the rows to delete.
        logger (logging.Logger): logger instance.
    """

    e = create_engine(db_name)
    table = get_table(table_name, schema, e, logger)

    with e.begin() as connection:
        n_rows = len(ids_to_delete)
        if n_rows == 0:
            logger.info("No rows to delete, skipping.")

        else:
            utils.delete_rows(
                table=table,
                id_column=table_id_column,
                ids_to_delete=ids_to_delete,
                connection=connection,
                logger=logger,
            )
