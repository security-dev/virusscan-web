COMPOSE_COMMAND=docker compose -f compose.dev.yml

start: ## Start the development docker containers
	@echo "Starting Docker containers for development"
	@$(COMPOSE_COMMAND) up

stop: ## Stop Containers
	@$(COMPOSE_COMMAND) down

restart: stop start ## Restart Containers

start-bg:  ## Start the development docker containers in the background
	@$(COMPOSE_COMMAND) up -d

build: ## Build dev containers
	@$(COMPOSE_COMMAND) build --pull

ssh: ## SSH into running web container
	@$(COMPOSE_COMMAND) exec web bash

bash: ## Get a bash shell into the web container
	@$(COMPOSE_COMMAND) run --rm --no-deps web bash

manage: ## Run any manage.py command. E.g. `make manage ARGS='createsuperuser'`
	@$(COMPOSE_COMMAND) run --rm web uv run manage.py ${ARGS}

migrations: ## Create DB migrations in the container
	@$(COMPOSE_COMMAND) run --rm web uv run manage.py makemigrations

migrate: ## Run DB migrations in the container
	@$(COMPOSE_COMMAND) run --rm web uv run manage.py migrate

shell: ## Get a Django shell
	@$(COMPOSE_COMMAND) run --rm web uv run manage.py shell

test:
	@$(COMPOSE_COMMAND) run --rm web uv run pytest

.PHONY: help
.DEFAULT_GOAL := help

help:
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Catch-all rule to allow additional arguments in make commands
%:
	@:
