install:
		poetry install

build:
		poetry build

dev:
		poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
		poetry run flake8 page_analyzer

reinstall:
	        pip install --user --force-reinstall dist/*.whl
renderdb:
	PGPASSWORD=4pyF4rJ12ouCd5NRe78Eblx5k6nZ5yUt psql -h dpg-cfov6do2i3mo4bv71eq0-a.oregon-postgres.render.com -U page_analyzer_user page_analyzer

.PHONY: install build dev start lint reinstall renderdb
