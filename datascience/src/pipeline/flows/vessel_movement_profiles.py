import time
import uuid
from datetime import datetime
from typing import Tuple

import numpy as np
import prefect
from prefect import Flow, Parameter, case, task
from prefect.tasks.prefect import StartFlowRun

from src.pipeline.generic_tasks import extract, load
from src.pipeline.helpers.datetime import get_datetime_chunks
from src.pipeline.helpers.ports import get_ports_h3_set
from src.pipeline.helpers.spatial import analyze_vessel_route, get_h3_indices


# @task(checkpoint=False)
def extract_all_positions(start: str = "1 year", end: str = "0 days"):
    positions_iter = extract(
        db_name="monitorfish_remote",
        query_filepath="monitorfish/all_positions.sql",
        chunksize=1000000,
        params={"start": start, "end": end},
    )

    dtypes = {
        "cfr": "category",
        "external_immatriculation": "category",
        "ircs": "category",
    }

    for positions in positions_iter:
        yield positions.astype(dtypes)


# @task(checkpoint=False)
def tag_positions_at_port(positions):

    positions = positions.copy(deep=True)

    h3_indices = get_h3_indices(
        positions, lat="latitude", lon="longitude", resolution=7
    ).rename("h3")

    ports_h3_ids = get_ports_h3_set(resolution=7, k_ring=1)

    positions["is_at_port"] = np.isin(h3_indices.values, ports_h3_ids)

    return positions


# @task(checkpoint=False)
def compute_vessel_movement_profiles(positions, ports_h3_ids):
    return positions.groupby("cfr", observed=True).apply(
        lambda x: analyze_vessel_route(x, ports_h3_ids, 1)
    )


@task(checkpoint=False)
def load_vessel_movement_profiles(profiles):

    load(
        profiles,
        table_name="vessel_movement_profiles",
        schema="public",
        db_name="monitorfish_remote",
        logger=prefect.context.get("logger"),
        delete_before_insert=True,
    )


def wip_flow():
    positions = extract_all_positions("3 months")
    positions = tag_positions_at_port(positions)
    profiles = positions.groupby("cfr", observed=True).apply(
        lambda x: analyze_vessel_route(x, days_analyzed=1)
    )
    return profiles


@task(checkpoint=False)
def get_chunks(chunk_size: str, chunks_from_now: int) -> Tuple:
    logger = prefect.context.get("logger")
    utcnow = datetime.datetime.utcnow()
    chunks = get_datetime_chunks(
        chunk_size=chunk_size, chunks_from_now=chunks_from_now, now=utcnow
    )

    logger.info(chunks)
    return chunks


@task(checkpoint=False)
def delete():
    logger = prefect.context.get("logger")
    logger.info("Deleting existing chunks")


@task(checkpoint=False)
def extract_(id, start_datetime_utc, end_datetime_utc):
    logger = prefect.context.get("logger")
    logger.info(
        f"Extracting chunk {id} from {start_datetime_utc} to {end_datetime_utc}..."
    )
    time.sleep(3)
    logger.info(f"Chunk {id} from {start_datetime_utc} to {end_datetime_utc} extraced.")
    return [1, 2, 3]


@task(checkpoint=False)
def transform(data):
    logger = prefect.context.get("logger")
    logger.error(f"Transforming data {data}.")
    return data * 2


@task(checkpoint=False)
def load_(data):
    logger = prefect.context.get("logger")
    logger.info(f"Loading data {data}")


with Flow("Movement profiles chunk") as sub_flow:

    id = Parameter("id")
    start_datetime_utc = Parameter("start_datetime_utc")
    end_datetime_utc = Parameter("end_datetime_utc")

    data = extract_(id, start_datetime_utc, end_datetime_utc)
    transform(data)
    load_(data)


@task(checkpoint=False)
def make_flow_runs(chunk):

    parameters = {
        "id": chunk.id,
        "start_datetime_utc": chunk.start_datetime_utc,
        "end_datetime_utc": chunk.end_datetime_utc,
    }

    logger = prefect.context.get("logger")
    logger.info(f"Launching processing of chunk with parameters {parameters}")

    StartFlowRun(
        flow_name="Movement profiles chunk",
        project_name="Test project",
        parameters=parameters,
        wait=True,
    ).run(idempotency_key=uuid.uuid4().hex)


@task(checkpoint=False)
def run_flow(flow_run):
    flow_run.run(idempotency_key=uuid.uuid4().hex)


with Flow("Movement profiles") as flow:
    chunks_from_now = Parameter("chunks_from_now", default=1)
    chunk_size = Parameter("chunk_size", default="month")
    delete_existing_chunks = Parameter("delete_existing_chunks", default=False)

    with case(delete_existing_chunks, True):
        delete()

    chunks = get_chunks(chunk_size, chunks_from_now)
    make_flow_runs.map(chunks)


if __name__ == "__main__":
    sub_flow.register("Test project")
    flow.register("Test project")
