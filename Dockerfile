FROM prefecthq/prefect:0.15.7

COPY app /velib-harvester/app
ADD requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /velib-harvester/

CMD ["/bin/sh", "-c", "prefect agent local start --key ${PREFECT_CLOUD_API_KEY} --label dev --show-flow-logs --env S3_BUCKET_NAME=${S3_BUCKET_NAME} --name heroku-agent --no-hostname-label"]