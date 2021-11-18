run-flow:
	PYTHONPATH=. prefect run -p app/flows/flow.py

deploy-container:
	heroku container:push worker --app velib-status-app
	heroku container:release worker --app=velib-status-app

prefect-register:
	prefect register --project velib-harvester -m "app.flows.flow"