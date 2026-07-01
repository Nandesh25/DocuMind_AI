# DocuMind AI — common tasks
# Usage: make <target>

COMPOSE = docker compose

.PHONY: help setup up down build logs ps model migrate backend-dev frontend-dev clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Copy .env templates (root + backend) if missing
	@[ -f .env ] || cp .env.example .env
	@[ -f backend/.env ] || cp backend/.env.example backend/.env
	@echo "Environment files ready. Edit SECRET_KEY before deploying."

up: ## Build and start the full stack (detached)
	$(COMPOSE) up -d --build

down: ## Stop the stack
	$(COMPOSE) down

build: ## Build images without starting
	$(COMPOSE) build

logs: ## Follow logs for all services
	$(COMPOSE) logs -f

ps: ## Show running services
	$(COMPOSE) ps

model: ## Pull the Ollama chat model
	$(COMPOSE) exec ollama ollama pull qwen2.5:3b

migrate: ## Apply Alembic migrations inside the api container
	$(COMPOSE) exec api alembic upgrade head

backend-dev: ## Run the backend locally (needs venv + deps)
	cd backend && uvicorn app.main:app --reload

frontend-dev: ## Run the frontend dev server
	cd frontend && npm start

clean: ## Stop the stack and remove volumes (DESTROYS DATA)
	$(COMPOSE) down -v
