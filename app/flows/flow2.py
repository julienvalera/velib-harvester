import pathlib
import sys

import prefect
from prefect import Flow, task
from prefect.storage import GitHub

logger = prefect.context.get("logger")

github_storage = GitHub(
    repo="julienvalera/velib-harvester",  # name of repo
    path="app/flows/flow2.py",  # location of flow file in repo
    access_token_secret="GITHUB_ACCESS_TOKEN",  # name of personal access token secret
)


@task
def show_result():
    logger.info(sys.path)
    logger.info("Salut")
    logger.info(pathlib.Path(__file__).parent)
    logger.info([file for file in pathlib.Path(__file__).parent.rglob("*")])


with Flow("Test", storage=github_storage) as flow:
    result = show_result()
