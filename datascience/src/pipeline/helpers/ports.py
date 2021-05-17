import h3

from src.pipeline.generic_tasks import extract
from src.pipeline.helpers.spatial import get_h3_indices


def get_ports_h3_set(resolution: int = 7, k_ring: int = 0) -> set:

    ports = extract(
        db_name="monitorfish_remote", query_filepath="monitorfish/ports_locations.sql"
    )

    ports["h3"] = get_h3_indices(
        ports, lat="latitude", lon="longitude", resolution=resolution
    )

    if k_ring > 0:
        ports["h3"] = ports.h3.map(lambda h: h3.k_ring(h, k_ring))
        ports = ports.explode("h3")
        ports = ports.reset_index().drop(columns=["index"])

    return set(ports.h3)
