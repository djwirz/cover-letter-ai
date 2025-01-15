.PHONY: setup start stop run clean

setup: ## Setup Python environment
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

start: ## Start Supabase
	supabase start

stop: ## Stop Supabase
	supabase stop

run: ## Run FastAPI server
	uvicorn app.main:app --reload

clean: ## Clean up environment
	find . -type d -name "__pycache__" -exec rm -rf {} +
	supabase stop

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help