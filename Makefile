.PHONY: help install test run docker-up docker-down clean lint format

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make run         - Run API locally"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make clean       - Clean cache files"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"

install:
	pip install -r requirements.txt

test:
	pytest task1/test_main.py -v

test-cov:
	pytest task1/test_main.py -v --cov=task1 --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

run:
	uvicorn task1.main:app --reload --port 8000

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf htmlcov .coverage
	rm -f users_*.csv

lint:
	@echo "Running flake8..."
	flake8 task1/ task2/ task3/ --max-line-length=120

format:
	@echo "Formatting with black..."
	black task1/ task2/ task3/ --line-length=120