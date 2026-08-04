.PHONY: install run test lint format clean

install:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -xvs

lint:
	ruff check app/ tests/
	mypy app/

format:
	ruff format app/ tests/

clean:
	docker-compose down -v
	rm -rf .pytest_cache __pycache__ .mypy_cache .ruff_cache
