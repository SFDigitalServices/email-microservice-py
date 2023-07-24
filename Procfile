web: bin/qgtunnel pipenv run gunicorn 'service.microservice:start_service()'
worker: bin/qgtunnel pipenv run celery worker -Ofair
release: bin/qgtunnel pipenv run alembic upgrade head