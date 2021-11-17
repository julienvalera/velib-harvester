from typing import Iterable

import pytest
from pydantic import ValidationError

from app.models.station_information import Data, Station, StationInformation


def test_deserialize_when_empty_dict_then_raise_validation_error():
    # WHEN THEN
    with pytest.raises(
        ValidationError,
        match="value_error.missing",
    ):
        StationInformation(**{})


def test_deserialize_when_dict_is_valid():
    # WHEN
    deserialized = StationInformation(
        **{
            "lastUpdatedOther": 0,
            "ttl": 3600,
            "data": {
                "stations": [
                    {
                        "station_id": 1,
                        "name": "Place du marché",
                        "lat": 48.0,
                        "lon": 13.0,
                        "capacity": 50,
                        "stationCode": "XXXXX",
                    },
                ]
            },
        }
    )

    # THEN
    assert isinstance(deserialized, StationInformation)
    assert deserialized.last_updated_other == 0
    assert deserialized.ttl == 3600
    assert isinstance(deserialized.data, Data)
    assert isinstance(deserialized.data.stations, Iterable)
    assert len(deserialized.data.stations) == 1
    assert isinstance(deserialized.data.stations[0], Station)
    assert deserialized.data.stations[0].station_id == 1
    assert deserialized.data.stations[0].name == "Place du marché"
    assert deserialized.data.stations[0].lat == 48.0
    assert deserialized.data.stations[0].lon == 13.0
    assert deserialized.data.stations[0].capacity == 50
    assert deserialized.data.stations[0].station_code == "XXXXX"


def test_deserialize_when_extra_field_then_raise_validation_error():
    # WHEN THEN
    with pytest.raises(
        ValidationError,
        match="extra fields not permitted",
    ):
        StationInformation(
            **{
                "lastUpdatedOther": 0,
                "ttl": 3600,
                "extraField": "value",
                "data": {
                    "stations": [
                        {
                            "station_id": 1,
                            "name": "Place du marché",
                            "lat": 48.0,
                            "lon": 13.0,
                            "capacity": 50,
                            "stationCode": "XXXXX",
                        },
                    ]
                },
            }
        )


def test_deserialize_when_wrong_type_field_then_raise_validation_error():
    # GIVEN
    wrong_value = "value"

    # WHEN THEN
    with pytest.raises(
        ValidationError,
        match="value is not a valid integer",
    ):
        StationInformation(
            **{
                "lastUpdatedOther": 0,
                "ttl": wrong_value,
                "data": {
                    "stations": [
                        {
                            "station_id": 1,
                            "name": "Place du marché",
                            "lat": 48.0,
                            "lon": 13.0,
                            "capacity": 50,
                            "stationCode": "XXXXX",
                        },
                    ]
                },
            }
        )


def test_serialize_when_dict_is_valid():
    # WHEN
    deserialized = StationInformation(
        **{
            "lastUpdatedOther": 0,
            "ttl": 3600,
            "data": {
                "stations": [
                    {
                        "station_id": 1,
                        "name": "Place du marché",
                        "lat": 48.0,
                        "lon": 13.0,
                        "capacity": 50,
                        "stationCode": "XXXXX",
                    },
                ]
            },
        }
    ).dict()

    # THEN
    data = deserialized.pop("data")
    assert "stations" in data.keys()
    assert len(data.keys()) == 1
    assert len(data["stations"]) == 1
    assert {
        "station_id": 1,
        "name": "Place du marché",
        "lat": 48.0,
        "lon": 13.0,
        "capacity": 50,
        "station_code": "XXXXX",
        "rental_methods": None,
    } in data["stations"]
    assert deserialized == {"last_updated_other": 0, "ttl": 3600}
