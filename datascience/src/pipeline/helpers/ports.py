import pickle

import h3

from config import LIBRARY_LOCATION
from src.pipeline.generic_tasks import extract
from src.pipeline.helpers.spatial import get_h3_indices, get_k_ring_of_h3_set


def get_ports_h3_dict() -> dict:

    ports = extract(
        db_name="monitorfish_remote", query_filepath="monitorfish/ports_locations.sql"
    )

    # Extract indices of h3 hexagons where some vessels have remained stationary
    # and which could be attributed to a known port

    ports_stationary_h3_cells = ports.loc[
        ports.stationary_vessels_h3_res9.map(len) != 0,
        ["stationary_vessels_h3_res9", "locode"],
    ]

    ports_stationary_h3_cells["stationary_vessels_h3_res9"] = ports_stationary_h3_cells[
        "stationary_vessels_h3_res9"
    ].map(lambda h3_list: get_k_ring_of_h3_set(h3_list, 1))

    ports_stationary_h3_cells_dict = (
        ports_stationary_h3_cells.rename(columns={"stationary_vessels_h3_res9": "h3"})
        .explode("h3")
        .set_index("h3")["locode"]
        .to_dict()
    )

    # Extract indices of h3 hexagons around the geocoded latitude / longitude of ports
    # for which the location could not be determined by the presence of stationary
    # vessels
    ports_geocoded_h3_cells = ports.loc[
        ports.stationary_vessels_h3_res9.map(len) == 0,
        ["latitude", "longitude", "locode"],
    ]
    ports_geocoded_h3_cells["h3"] = get_h3_indices(
        ports_geocoded_h3_cells, resolution=9
    )

    ports_geocoded_h3_cells["h3"] = ports_geocoded_h3_cells.h3.map(
        lambda h: h3.k_ring(h, 2)
    )

    ports_geocoded_h3_cells_dict = (
        ports_geocoded_h3_cells[["locode", "h3"]]
        .explode("h3")
        .set_index("h3")["locode"]
        .to_dict()
    )

    # Extract indices of h3 hexagons where some vessels have remained stationary
    # but could not be attributed to a known port
    pickle_path = "pipeline/data/unknown_port_stationary_vessels_h3_res9.pkl"
    with open(LIBRARY_LOCATION / pickle_path, "rb") as pickled_file:
        unknown_port_stationary_vessels_h3_res9 = pickle.load(pickled_file)

    unknown_port_stationary_vessels_h3_res9 = get_k_ring_of_h3_set(
        unknown_port_stationary_vessels_h3_res9, k=1
    )
    unknown_port_h3_cells_dict = {
        hexagon: "Port inconnu" for hexagon in unknown_port_stationary_vessels_h3_res9
    }

    # Merge into one dict
    res = {
        **unknown_port_h3_cells_dict,
        **ports_geocoded_h3_cells_dict,
        **ports_stationary_h3_cells_dict,
    }

    return res
