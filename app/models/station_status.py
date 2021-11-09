from typing import List, Optional, Union

from pydantic import BaseModel, Extra, validator


class NumBikesAvailableTypeMechanical(BaseModel, extra=Extra.forbid):
    mechanical: int


class NumBikesAvailableTypeElectrical(BaseModel, extra=Extra.forbid):
    ebike: int


class Station(BaseModel, extra=Extra.forbid):
    stationCode: str
    station_id: Optional[int]
    num_bikes_available: int
    numBikesAvailable: int
    num_bikes_available_types: List[
        Union[NumBikesAvailableTypeMechanical, NumBikesAvailableTypeElectrical]
    ]
    num_docks_available: int
    numDocksAvailable: int
    is_installed: int
    is_returning: int
    is_renting: int
    last_reported: int

    @validator("num_bikes_available_types")
    def num_bikes_available_types_must_contain_both_types(cls, available_types):
        if len(available_types) != 2:
            raise ValueError("Must contain two available types")
        elif [key for type in available_types for key in type.dict().keys()] != [
            "mechanical",
            "ebike",
        ]:
            raise ValueError("Must contain both mechanical and eletrical types")
        return available_types


class Data(BaseModel, extra=Extra.forbid):
    stations: List[Station]


class StationStatus(BaseModel, extra=Extra.forbid):
    lastUpdatedOther: int
    ttl: int
    data: Data
