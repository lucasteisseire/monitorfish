import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import sqlalchemy

from config import default_risk_factors
from src.pipeline.flows.last_positions import (
    add_vessel_identifier,
    compute_emission_period,
    concatenate,
    drop_unchanched_new_last_positions,
    estimate_current_positions,
    extract_last_positions,
    extract_previous_last_positions,
    extract_risk_factors,
    flow,
    load_last_positions,
    merge_last_positions_risk_factors,
    split,
    tag_vessels_at_port,
    validate_action,
)
from tests.mocks import mock_extract_side_effect


class TestLastPositionsFlow(unittest.TestCase):
    @patch("src.pipeline.flows.last_positions.extract")
    def test_extract_risk_factors(self, mock_extract):
        mock_extract.side_effect = mock_extract_side_effect
        query = extract_risk_factors.run()
        self.assertTrue(isinstance(query, sqlalchemy.sql.elements.TextClause))

    @patch("src.pipeline.flows.last_positions.extract")
    def test_extract_previous_last_positions(self, mock_extract):
        mock_extract.side_effect = mock_extract_side_effect
        query = extract_previous_last_positions.run()
        self.assertTrue(isinstance(query, sqlalchemy.sql.elements.TextClause))

    @patch("src.pipeline.flows.last_positions.extract")
    def test_extract_last_positions(self, mock_extract):
        mock_extract.side_effect = mock_extract_side_effect
        query = extract_last_positions.run(minutes=10)
        self.assertTrue(isinstance(query, sqlalchemy.sql.elements.TextClause))

    @patch("src.pipeline.flows.last_positions.load", autospec=True)
    def test_load_last_positions(self, mock_load):
        dummy_last_positions = pd.DataFrame()
        load_last_positions.run(dummy_last_positions)

    def test_validate_action(self):
        self.assertEqual(validate_action.run("update"), "update")
        self.assertEqual(validate_action.run("replace"), "replace")
        with self.assertRaises(ValueError):
            validate_action.run("unknown_option")

    def test_drop_unchanched_new_last_positions(self):
        previous_last_positions = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "vessel_id": ["A", "B", "C", "D"],
                "some": [1.1, 0.2, -5.65, 1],
                "more": ["b", "c", "d", "a"],
                "data": [None, None, None, None],
            }
        )

        new_last_positions = pd.DataFrame(
            {
                "id": [4, 5, 6],
                "vessel_id": ["D", "E", "A"],
                "some": [1.8, 2.2, -1.1],
                "more": ["a", "d", "f"],
                "data": [None, 42, ""],
            }
        )

        expected_res = pd.DataFrame(
            {
                "id": [5, 6],
                "vessel_id": ["E", "A"],
                "some": [2.2, -1.1],
                "more": ["d", "f"],
                "data": [42, ""],
            }
        )

        res = drop_unchanched_new_last_positions.run(
            new_last_positions, previous_last_positions
        )

        self.assertEqual(list(res), list(expected_res))
        self.assertEqual(res.values.tolist(), expected_res.values.tolist())

    def test_split(self):
        previous_last_positions = pd.DataFrame(
            {
                "cfr": ["A", "B", "C", None, None, "G", "H", "H"],
                "external_immatriculation": [
                    "AA",
                    "BB",
                    None,
                    "DD",
                    None,
                    "GG",
                    "HH",
                    "H-H",
                ],
                "ircs": ["AAA", None, None, None, "EEE", "GGG", "HHH", "HHH"],
                "last_position_datetime_utc": [
                    datetime(2021, 10, 1, 20, 52, 10),
                    datetime(2021, 10, 1, 20, 42, 10),
                    datetime(2021, 10, 1, 20, 32, 10),
                    datetime(2021, 10, 1, 19, 52, 10),
                    datetime(2021, 10, 1, 20, 16, 10),
                    datetime(2021, 10, 1, 19, 16, 55),
                    datetime(2021, 10, 1, 19, 16, 55),
                    datetime(2021, 10, 1, 19, 16, 55),
                ],
            }
        )

        new_last_positions = pd.DataFrame(
            {
                "cfr": ["A", None, "F", "G", "H", "H"],
                "external_immatriculation": ["AA", None, "FF", "GG", "HH", "H-H"],
                "ircs": ["AAA", "EEE", None, None, "HHH", "HHH"],
                "last_position_datetime_utc": [
                    datetime(2021, 10, 1, 21, 52, 10),
                    datetime(2021, 10, 1, 21, 56, 10),
                    datetime(2021, 10, 1, 21, 54, 10),
                    datetime(2021, 10, 1, 20, 17, 25),
                    datetime(2021, 10, 1, 20, 16, 55),
                    datetime(2021, 10, 1, 20, 16, 55),
                ],
                "some": [1, 2, 3, 4, 5, 6],
                "more": ["a", "b", "c", "g", "h", "i"],
                "data": [None, 2.256, "Bla", "Picachu", "What", "Not"],
            }
        )

        (
            unchanged_previous_last_positions,
            new_vessels_last_positions,
            last_positions_to_update,
        ) = split.run(previous_last_positions, new_last_positions)

        print()
        print("unchanged_previous_last_positions")
        print()
        print(unchanged_previous_last_positions)
        print()

        print()
        print("new_vessels_last_positions")
        print()
        print(new_vessels_last_positions)
        print()

        print()
        print("last_positions_to_update")
        print()
        print(last_positions_to_update)
        print()

        expected_unchanged_previous_last_positions = previous_last_positions.iloc[
            [1, 2, 3]
        ]

        expected_new_vessels_last_positions = new_last_positions.iloc[[2]]

        expected_last_positions_to_update = pd.DataFrame(
            {
                "cfr": ["A", "G", None],
                "external_immatriculation": ["AA", "GG", None],
                "ircs": ["AAA", "GGG", "EEE"],
                "last_position_datetime_utc_previous": [
                    datetime(2021, 10, 1, 20, 52, 10),
                    datetime(2021, 10, 1, 19, 16, 55),
                    datetime(2021, 10, 1, 20, 16, 10),
                ],
                "last_position_datetime_utc_new": [
                    datetime(2021, 10, 1, 21, 52, 10),
                    datetime(2021, 10, 1, 20, 17, 25),
                    datetime(2021, 10, 1, 21, 56, 10),
                ],
                "some": [1, 4, 2],
                "more": ["a", "g", "b"],
                "data": [None, "Picachu", 2.256],
            },
        ).astype({"data": "object"})

        pd.testing.assert_frame_equal(
            unchanged_previous_last_positions,
            expected_unchanged_previous_last_positions,
        )

        pd.testing.assert_frame_equal(
            new_vessels_last_positions, expected_new_vessels_last_positions
        )

        pd.testing.assert_frame_equal(
            last_positions_to_update, expected_last_positions_to_update
        )

    def test_compute_emission_period(self):
        last_positions_to_update = pd.DataFrame(
            {
                "cfr": ["A", None],
                "external_immatriculation": ["AA", None],
                "ircs": ["AAA", "EEE"],
                "last_position_datetime_utc_previous": [
                    datetime(2021, 10, 1, 20, 52, 10),
                    datetime(2021, 10, 1, 20, 16, 10),
                ],
                "last_position_datetime_utc_new": [
                    datetime(2021, 10, 1, 21, 52, 10),
                    datetime(2021, 10, 1, 21, 56, 10),
                ],
                "emission_period": [timedelta(minutes=10), None],
                "some": [1, 2],
                "more": ["a", "b"],
                "data": [None, 2.256],
            },
        )

        updated_last_positions = compute_emission_period.run(last_positions_to_update)

        expected_updated_last_positions = pd.DataFrame(
            {
                "cfr": ["A", None],
                "external_immatriculation": ["AA", None],
                "ircs": ["AAA", "EEE"],
                "last_position_datetime_utc": [
                    datetime(2021, 10, 1, 21, 52, 10),
                    datetime(2021, 10, 1, 21, 56, 10),
                ],
                "emission_period": [
                    timedelta(minutes=10),
                    timedelta(hours=1, minutes=40),
                ],
                "some": [1, 2],
                "more": ["a", "b"],
                "data": [None, 2.256],
            },
        )

        self.assertTrue(updated_last_positions.equals(expected_updated_last_positions))

    def test_concatenate(self):

        unchanged_previous_last_positions = pd.DataFrame(
            {
                "vessel_id": ["A", "B", "C"],
                "some": [1, 2, None],
                "more": ["a", None, "c"],
                "data": [None, 2.256, 0.1],
            }
        )

        new_vessels_last_positions = pd.DataFrame(
            {"vessel_id": ["D"], "some": [1], "more": ["d"], "data": [2.36]}
        )

        updated_last_positions = pd.DataFrame(
            {
                "vessel_id": ["E", "F"],
                "some": [1, 2],
                "more": ["e", "f"],
                "data": [None, 21.256],
            }
        )

        expected_last_positions = pd.DataFrame(
            {
                "vessel_id": ["A", "B", "C", "D", "E", "F"],
                "some": [1, 2, None, 1, 1, 2],
                "more": ["a", None, "c", "d", "e", "f"],
                "data": [None, 2.256, 0.1, 2.36, None, 21.256],
            }
        )

        last_positions = concatenate.run(
            unchanged_previous_last_positions,
            new_vessels_last_positions,
            updated_last_positions,
        )

        self.assertTrue(last_positions.equals(expected_last_positions))

    @patch("src.pipeline.flows.last_positions.datetime")
    def test_estimate_current_positions(self, mock_datetime):

        mock_datetime.utcnow = lambda: datetime(2021, 10, 1, 10, 0, 0)

        last_positions = pd.DataFrame(
            {
                "latitude": [45, 45.1, 45.2, 45.3],
                "longitude": [-5, -5.1, -5.2, -5.3],
                "course": [0, 45, "invalid", 180],
                "speed": [0, 5, 10, 10.2],
                "last_position_datetime_utc": [
                    datetime(2021, 10, 1, 0, 0, 0),
                    datetime(2021, 10, 1, 9, 0, 0),
                    datetime(2021, 10, 1, 9, 30, 0),
                    datetime(2021, 10, 1, 10, 0, 10),
                ],
            }
        )

        expected_estimated_current_positions = last_positions.copy(deep=True)
        expected_estimated_current_positions["estimated_current_latitude"] = [
            None,
            45.158888,
            None,
            None,
        ]
        expected_estimated_current_positions["estimated_current_longitude"] = [
            None,
            -5.016725,
            None,
            None,
        ]

        estimated_current_positions = estimate_current_positions.run(
            last_positions=last_positions, max_hours_since_last_position=1.5
        )

        pd.testing.assert_frame_equal(
            estimated_current_positions, expected_estimated_current_positions
        )

    def test_merge_last_positions_risk_factors(self):

        last_positions = pd.DataFrame(
            {
                "cfr": ["A", "B", None, None],
                "ircs": ["aa", "bb", "cc", None],
                "external_immatriculation": ["aaa", None, None, "ddd"],
                "latitude": [45, 45.12, 56.214, 21.325],
                "longitude": [-5.1236, -12.85, 1.01, -1.236],
            }
        )

        risk_factors = pd.DataFrame(
            {
                "cfr": ["A", None, None, "E"],
                "ircs": ["aa", "cc", None, "ee"],
                "external_immatriculation": ["aaa", None, "ddd", "eee"],
                "impact_risk_factor": [1.2, 3.8, 1.2, 3.7],
                "probability_risk_factor": [1.3, 1.5, 2.1, 2.2],
                "detectability_risk_factor": [2.1, 2.3, 2.3, 1.4],
                "risk_factor": [1.8, 3.0, 1.9, 3.3],
                "total_weight_onboard": [121.2, None, None, 4.0],
            }
        )

        res = merge_last_positions_risk_factors.run(last_positions, risk_factors)

        res = (
            res.sort_values(["cfr", "ircs", "external_immatriculation"])
            .reset_index()
            .drop(columns=["index"])
        )

        expected_res = pd.DataFrame(
            {
                "cfr": ["A", "B", None, None],
                "ircs": ["aa", "bb", "cc", None],
                "external_immatriculation": ["aaa", None, None, "ddd"],
                "latitude": [45, 45.12, 56.214, 21.325],
                "longitude": [-5.1236, -12.85, 1.01, -1.236],
                "impact_risk_factor": [1.2, None, 3.8, 1.2],
                "probability_risk_factor": [1.3, None, 1.5, 2.1],
                "detectability_risk_factor": [2.1, None, 2.3, 2.3],
                "risk_factor": [1.8, None, 3.0, 1.9],
                "total_weight_onboard": [121.2, 0.0, 0.0, 0.0],
            }
        ).fillna({**default_risk_factors})

        pd.testing.assert_frame_equal(expected_res, res)

    @patch("src.pipeline.flows.last_positions.extract")
    def test_tag_vessels_at_port(self, mock_extract):

        mock_extract.return_value = pd.DataFrame(
            {
                "h3": [
                    "8900510a463ffff",
                    "892b2c359d3ffff",
                    "some_other_h3_cell",
                ],
            }
        )

        last_positions = pd.DataFrame(
            {
                "latitude": [45, 85.1, -85.2, 45.3, 45.4],
                "longitude": [89.1, 10, -10, 12.6, -59.16],
            }
        )

        last_positions_with_is_at_port = tag_vessels_at_port.run(last_positions)

        expected_last_positions_with_is_at_port = last_positions.copy().assign(
            is_at_port=[False, True, False, False, True]
        )

        pd.testing.assert_frame_equal(
            last_positions_with_is_at_port, expected_last_positions_with_is_at_port
        )

    @patch("src.pipeline.flows.last_positions.extract")
    def test_tag_vessels_at_port_empty_dataframe(self, mock_extract):

        last_positions = pd.DataFrame(
            {
                "latitude": [],
                "longitude": [],
            }
        ).astype({"latitude": float, "longitude": float})

        last_positions_with_is_at_port = tag_vessels_at_port.run(last_positions)

        # Query should not be run with empty list in WHERE condition
        mock_extract.assert_not_called()

        expected_last_positions_with_is_at_port = pd.DataFrame(
            columns=pd.Index(["latitude", "longitude", "is_at_port"])
        ).astype({"latitude": float, "longitude": float, "is_at_port": bool})

        pd.testing.assert_frame_equal(
            last_positions_with_is_at_port,
            expected_last_positions_with_is_at_port,
            check_index_type=False,
        )

    def test_add_vessel_identifier(self):

        last_positions = pd.DataFrame(
            {
                "cfr": ["A", "B", None, None, None],
                "ircs": ["aa", "bb", "cc", None, "ee"],
                "external_immatriculation": ["aaa", None, None, "ddd", "eee"],
                "some": [1, 2, None, 1, 1],
                "more": ["a", None, "c", "d", "e"],
                "data": [None, 2.256, 0.1, 2.36, None],
            }
        )

        last_positions_with_vessel_identifier = add_vessel_identifier.run(
            last_positions
        )

        expected_last_positions_with_vessel_identifier = last_positions.copy(
            deep=True
        ).assign(
            vessel_identifier=[
                "INTERNAL_REFERENCE_NUMBER",
                "INTERNAL_REFERENCE_NUMBER",
                "IRCS",
                "EXTERNAL_REFERENCE_NUMBER",
                "IRCS",
            ]
        )

        pd.testing.assert_frame_equal(
            last_positions_with_vessel_identifier,
            expected_last_positions_with_vessel_identifier,
        )
