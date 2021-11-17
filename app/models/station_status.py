from typing import Any, List, Optional, Union

from pydantic import BaseModel, Extra, Field, validator


class NumBikesAvailableTypeMechanical(BaseModel, extra=Extra.forbid):
    num_mechanical_bikes: int = Field(None, alias="mechanical")


class NumBikesAvailableTypeElectrical(BaseModel, extra=Extra.forbid):
    num_e_bikes: int = Field(None, alias="ebike")


class Station(BaseModel, extra=Extra.forbid):

    station_code: str = Field(None, alias="stationCode")
    station_id: Optional[int]
    num_bikes_available: int
    num_bikes_available_types: List[
        Union[NumBikesAvailableTypeMechanical, NumBikesAvailableTypeElectrical]
    ]
    num_docks_available: int
    is_installed: int
    is_returning: int
    is_renting: int
    last_reported: int

    def __init__(
        self,
        *,
        stationCode: str,
        station_id: Optional[int],
        num_bikes_available: int,
        num_bikes_available_types: List[
            Union[
                NumBikesAvailableTypeMechanical,
                NumBikesAvailableTypeElectrical,
            ]
        ],
        num_docks_available: int,
        is_installed: int,
        is_returning: int,
        is_renting: int,
        last_reported: int,
        # Duplicate fields. Ignore them
        numBikesAvailable: int,
        numDocksAvailable: int,
        **data
    ) -> None:
        super().__init__(
            stationCode=stationCode,
            station_id=station_id,
            num_bikes_available=num_bikes_available,
            num_bikes_available_types=num_bikes_available_types,
            num_docks_available=num_docks_available,
            is_installed=is_installed,
            is_returning=is_returning,
            is_renting=is_renting,
            last_reported=last_reported,
            **data,
        )

    @validator("num_bikes_available_types")
    def num_bikes_available_types_must_contain_both_types(
        cls, available_types
    ):
        if len(available_types) != 2:
            raise ValueError("Must contain two available types")
        return available_types


class Data(BaseModel, extra=Extra.forbid):
    stations: List[Station]


class StationStatus(BaseModel, extra=Extra.forbid):
    last_updated_other: int = Field(None, alias="lastUpdatedOther")
    ttl: int
    data: Data
