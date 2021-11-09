from typing import List, Optional

from pydantic import BaseModel, Extra


class Station(BaseModel):
    class Config:
        extra = "forbid"

    station_id: int
    name: str
    lat: float
    lon: float
    capacity: int
    stationCode: str
    rental_methods: Optional[List[str]]


class Data(BaseModel, extra=Extra.forbid):
    stations: List[Station]


class StationInformation(BaseModel, extra=Extra.forbid):
    lastUpdatedOther: int
    ttl: int
    data: Data
