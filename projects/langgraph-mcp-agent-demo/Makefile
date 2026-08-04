.PHONY: install dev test lint format index run clean

install:
	pip install -e ".[dev]"

dev:
	docker-compose up -d
	python -m app.main

test:
	pytest -xvs --cov=app

lint:
	ruff check app/ tests/
	mypy app/

format:
	ruff format app/ tests/

index:
	python -m app.rag.indexer

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	docker-compose down -v
	rm -rf .pytest_cache __pycache__ .mypy_cache
