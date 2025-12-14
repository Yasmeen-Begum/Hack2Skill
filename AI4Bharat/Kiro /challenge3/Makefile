.PHONY: help install dev-install test lint format type-check clean run-api run-ui setup

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Initial project setup
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\\Scripts\\activate     (Windows)"

install:  ## Install production dependencies
	pip install -r requirements.txt

dev-install:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:  ## Run tests
	pytest -v

test-watch:  ## Run tests in watch mode
	pytest -v --tb=short -x --looponfail

lint:  ## Run linting
	flake8 weather_stock_dashboard tests config
	black --check weather_stock_dashboard tests config

format:  ## Format code
	black weather_stock_dashboard tests config

type-check:  ## Run type checking
	mypy weather_stock_dashboard config

clean:  ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

run-api:  ## Run the FastAPI server
	python main.py

run-ui:  ## Run the Gradio interface (when implemented)
	@echo "Gradio interface not yet implemented"

check-all: lint type-check test  ## Run all checks

install-pre-commit:  ## Install pre-commit hooks
	pip install pre-commit
	pre-commit install