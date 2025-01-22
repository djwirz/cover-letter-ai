.PHONY: setup start stop run clean db-init test test-v test-cov lint format help install-dev

setup: ## Setup Python environment
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install-dev: ## Install development dependencies
	. venv/bin/activate && pip install -r requirements-dev.txt

start: ## Start Supabase
	supabase start

stop: ## Stop Supabase
	supabase stop

db-init: ## Initialize database schema
	PGPASSWORD=postgres psql -h localhost -U postgres -p 54322 -d postgres -f init.sql

run: ## Run FastAPI server
	uvicorn app.main:app --reload

clean: ## Clean up environment
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	supabase stop

test: ## Run tests
	pytest tests/

test-v: ## Run tests with verbose output
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

test-unit: ## Run only unit tests
	pytest tests/test_*_analysis.py -v

test-api: ## Run only API tests
	pytest tests/test_routes.py -v

lint: ## Run linter
	flake8 app/ tests/
	mypy app/ tests/

format: ## Format code
	black app/ tests/
	isort app/ tests/

check: ## Run all checks (format, lint, test)
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test-cov

dev-setup: ## Setup complete development environment
	$(MAKE) setup
	$(MAKE) install-dev
	$(MAKE) start
	$(MAKE) db-init

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help