lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest 

test-local:
	poetry run python3 -m pytest

install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

check:
	make lint
	make test

test-coverage:
	poetry run python3 -m pytest --cov=page_analyzer --cov-report=xml

build:
	./build.sh

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

package-force-reinstall:
	python3 -m pip install --user dist/*.whl --force-reinstall