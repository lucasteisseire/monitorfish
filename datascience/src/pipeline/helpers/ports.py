import pickle

import h3

from config import LIBRARY_LOCATION
from src.pipeline.generic_tasks import extract
from src.pipeline.helpers.spatial import get_h3_indices


def get_ports_h3_dict() -> dict:

    # Take indices of h3 hexagons where some vessels have been station
    pickle_path = "pipeline/data/unknown_port_stationary_vessels_h3_res9.pkl"
    with open(LIBRARY_LOCATION / pickle_path, "rb") as pickled_file:
        unknown_port_stationary_vessels_h3_res9 = pickle.load(pickled_file)

    res = {
        hexagon: "Port inconnu" for hexagon in unknown_port_stationary_vessels_h3_res9
    }

    ports = extract(
        db_name="monitorfish_remote", query_filepath="monitorfish/ports_locations.sql"
    )

    ports["h3"] = get_h3_indices(ports, lat="latitude", lon="longitude", resolution=9)

    ports["h3"] = ports.h3.map(lambda h: h3.k_ring(h, 4))
    ports = ports.explode("h3")
    ports = ports.reset_index().drop(columns=["index"])

    # TODO : merge ports and res

    return res
