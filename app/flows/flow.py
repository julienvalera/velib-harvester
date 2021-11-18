import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Type

import prefect
import requests
from prefect import Flow, case, task
from prefect.engine.results import LocalResult
from prefect.run_configs import LocalRun
from prefect.storage import Module
from prefect.tasks.aws.s3 import S3Upload
from pydantic.main import BaseModel

from app.models.station_information import StationInformation
from app.models.station_status import StationStatus

VELIB_API_URL = (
    "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole"
)
LOCAL_RESULT_PATH = Path("app/results.txt")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

logger = prefect.context.get("logger")

local_result = LocalResult(
    dir=str(LOCAL_RESULT_PATH.parent),
    location=str(LOCAL_RESULT_PATH.name),
)

module_storage = Module(module=__name__)


class S3UploadVelibData(S3Upload):
    def __init__(
        self,
        bucket: str = None,
        boto_kwargs: dict = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(bucket=bucket, boto_kwargs=boto_kwargs, **kwargs)

    def run(self, data: str, **kwargs: Any) -> str:
        key_name = self.define_s3_key_name(data["last_updated_other"])
        super().run(data=json.dumps(data), key=key_name, **kwargs)

    def define_s3_key_name(self, last_update: int) -> str:
        last_update_dt = datetime.fromtimestamp(last_update)
        return f"{last_update_dt.year}/{last_update_dt.month}/{last_update_dt.day}/{last_update_dt:%Y-%m-%d-%H_%M_%S}_velibstatus.json"


@task
def fetch_station_status_data() -> Dict[str, Any]:
    response = requests.get(f"{VELIB_API_URL}/station_status.json")
    response.raise_for_status()
    return response.json()


@task
def fetch_station_information_data() -> Dict[str, Any]:
    response = requests.get(f"{VELIB_API_URL}/station_information.json")
    response.raise_for_status()
    return response.json()


@task
def validate_schema(
    schema: Type[BaseModel], data: Dict[str, Any]
) -> BaseModel:
    return schema(**data).dict()


@task
def sort_by_station_id(station_information: Dict[str, Any]) -> Dict[str, Any]:
    stations_by_station_id = {}
    for station in station_information["data"]["stations"]:
        stations_by_station_id[station.pop("station_id")] = station
    return stations_by_station_id


@task
def merge_station_information_and_status(
    station_information: Dict[str, Any],
    station_status: Dict[str, Any],
) -> Dict[str, Any]:
    for station in station_status["data"]["stations"]:
        infos = station_information.get(station["station_id"])
        if infos is None:
            logger.warning(
                f"Missing station ID {station['station_id']} in station information."
            )
        station.update(infos)
    return station_status


@task
def flow_should_run(station_information: Dict[str, Any]) -> bool:
    try:
        previous_timestamp = local_result.read(
            location=LOCAL_RESULT_PATH.name
        ).value
    except Exception:
        previous_timestamp = 0
        logger.info(
            f"No result output exists yet. Create one with {previous_timestamp} as a default value."
        )
        local_result.write(previous_timestamp)
    current_timestamp = station_information["last_updated_other"]
    should_run = int(previous_timestamp) < int(current_timestamp)
    if not should_run:
        logger.info(
            "The flow will not be launched because API data has not yet been updated: "
            f"current_timestamp={current_timestamp}, previous_timestamp={previous_timestamp}"
        )
    local_result.write(current_timestamp)
    return should_run


with Flow("Velib Harvester", storage=module_storage) as flow:
    # Load Velib station information
    station_information_json = fetch_station_information_data()
    station_information = validate_schema(
        StationInformation,
        station_information_json,
        task_args=dict(name="validate_station_information"),
    )

    # Check whether the flow should run
    should_run = flow_should_run(station_information)

    with case(should_run, True):
        # Sort station information by station_id
        information_by_station_id = sort_by_station_id(station_information)

        # Load Velib station status
        station_status_json = fetch_station_status_data()
        station_status = validate_schema(
            StationStatus,
            station_status_json,
            task_args=dict(name="validate_station_status"),
        )

        # Merge status data and information data
        merged_data = merge_station_information_and_status(
            station_information=information_by_station_id,
            station_status=station_status,
        )

        # Upload data to S3 bucket
        upload_to_s3 = S3UploadVelibData(bucket=S3_BUCKET_NAME)
        upload_to_s3(data=merged_data)

flow.run_config = LocalRun(labels=["dev"])
