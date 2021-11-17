from typing import List, Optional

from pydantic import BaseModel, Extra, Field


class Station(BaseModel, extra=Extra.forbid):

    station_id: int
    name: str
    lat: float
    lon: float
    capacity: int
    station_code: str = Field(None, alias="stationCode")
    rental_methods: Optional[List[str]]


class Data(BaseModel, extra=Extra.forbid):
    stations: List[Station]


class StationInformation(BaseModel, extra=Extra.forbid):
    last_updated_other: int = Field(None, alias="lastUpdatedOther")
    ttl: int
    data: Data
