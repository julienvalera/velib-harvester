from typing import Iterable, List, Optional

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import from_type
from pydantic import BaseModel, ValidationError

from app.models.station_status import (
    Data,
    NumBikesAvailableTypeElectrical,
    NumBikesAvailableTypeMechanical,
    Station,
    StationStatus,
)


def test_deserialize_when_empty_dict_then_raise_validation_error():
    # WHEN THEN
    with pytest.raises(
        ValidationError,
        match="value_error.missing",
    ):
        StationStatus(**{})


def test_deserialize_and_ignore_duplicate_fields_when_dict_is_valid():
    # WHEN
    deserialized = StationStatus(
        **{
            "lastUpdatedOther": 0,
            "ttl": 3600,
            "data": {
                "stations": [
                    {
                        "stationCode": "XXXXX",
                        "station_id": 1,
                        "num_bikes_available": 0,
                        "numBikesAvailable": 0,
                        "num_bikes_available_types": [
                            {"mechanical": 0},
                            {"ebike": 0},
                        ],
                        "num_docks_available": 32,
                        "numDocksAvailable": 32,
                        "is_installed": 1,
                        "is_returning": 1,
                        "is_renting": 1,
                        "last_reported": 1636549998,
                    }
                ]
            },
        }
    )

    # THEN
    assert isinstance(deserialized, StationStatus)
    assert deserialized.last_updated_other == 0
    assert deserialized.ttl == 3600
    assert isinstance(deserialized.data, Data)
    assert isinstance(deserialized.data.stations, Iterable)
    assert len(deserialized.data.stations) == 1
    station = deserialized.data.stations[0]
    assert station.station_code == "XXXXX"
    assert station.station_id == 1
    assert station.num_bikes_available == 0
    assert isinstance(station.num_bikes_available_types, Iterable)
    assert len(station.num_bikes_available_types) == 2
    assert isinstance(
        station.num_bikes_available_types[0], NumBikesAvailableTypeMechanical
    )
    assert station.num_bikes_available_types[0].num_mechanical_bikes == 0
    assert isinstance(
        station.num_bikes_available_types[1], NumBikesAvailableTypeElectrical
    )
    assert station.num_bikes_available_types[1].num_e_bikes == 0
    assert station.num_docks_available == 32
    assert station.is_installed == 1
    assert station.is_returning == 1
    assert station.is_renting == 1
    assert station.last_reported == 1636549998
    assert not hasattr(station, "numBikesAvailable")
    assert not hasattr(station, "numDocksAvailable")


def test_num_bikes_available_types_must_contain_both_types_when_duplicate_available_types_then_raise_value_error():
    # WHEN
    with pytest.raises(
        ValidationError,
        match="Must contain two available types",
    ):
        Station(
            **{
                "stationCode": "XXXXX",
                "station_id": 1,
                "num_bikes_available": 0,
                "numBikesAvailable": 0,
                "num_bikes_available_types": [
                    {"mechanical": 0},
                    {"ebike": 0},
                    {"mechanical": 14},
                ],
                "num_docks_available": 32,
                "numDocksAvailable": 32,
                "is_installed": 1,
                "is_returning": 1,
                "is_renting": 1,
                "last_reported": 1636549998,
            }
        )
