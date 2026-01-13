.PHONY: all format lint test coverage build clean install install-wheel

all: help

coverage:
	poetry run pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered

format:
	poetry run black .

lint:
	poetry run black .
	poetry run flake8 . --config=.flake8 --output-file=lint-report.json

test:
	poetry run pytest tests

build:
	@echo "Building SDK..."
	cd sdk && poetry build
	@echo "Building CLI..."
	cd cli/highflame_cli && poetry build

build-sdk:
	cd sdk && poetry build

build-cli:
	cd cli/highflame_cli && poetry build

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf sdk/dist/ sdk/build/ sdk/*.egg-info/
	rm -rf cli/highflame_cli/dist/ cli/highflame_cli/build/ cli/highflame_cli/*.egg-info/

install:
	@echo "Installing SDK..."
	cd sdk && poetry install
	@echo "Installing CLI..."
	cd cli/highflame_cli && poetry install

install-sdk:
	cd sdk && poetry install

install-cli:
	cd cli/highflame_cli && poetry install

install-wheel:
	pip install sdk/dist/highflame-*.whl --force-reinstall
