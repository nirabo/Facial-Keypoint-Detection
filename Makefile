# Facial Keypoint Detection - Makefile
# ML project for facial keypoint detection using CNN and OpenCV

# Configuration
ENV ?= dev
PROJECT_NAME ?= facial-keypoints
SERVICE_NAME = jupyter

# Docker compose
COMPOSE_FILE = compose.yaml
ENV_FILE = .env.$(ENV)
DOCKER_COMPOSE_CMD = docker compose --env-file $(ENV_FILE)

# Colors
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
RESET := \033[0m

.DEFAULT_GOAL := help

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help:
	@echo "$(BLUE)[$(PROJECT_NAME)]$(RESET) - Facial Keypoint Detection"
	@echo ""
	@echo "$(YELLOW)Usage:$(RESET)"
	@echo "  make [target] [ENV=dev|prod]"
	@echo ""
	@echo "$(YELLOW)Environment:$(RESET)"
	@echo "  ENV=dev    Development environment (default)"
	@echo "  ENV=prod   Production environment"
	@echo ""
	@echo "$(YELLOW)Core Targets:$(RESET)"
	@echo "  $(GREEN)help$(RESET)              Show this help message"
	@echo "  $(GREEN)up$(RESET)                Start Jupyter Lab for development"
	@echo "  $(GREEN)down$(RESET)              Stop all services"
	@echo "  $(GREEN)restart$(RESET)           Restart services"
	@echo "  $(GREEN)logs$(RESET)              View logs"
	@echo "  $(GREEN)ps$(RESET)                List running services"
	@echo "  $(GREEN)build$(RESET)             Build Docker images"
	@echo "  $(GREEN)clean$(RESET)             Remove containers and volumes"
	@echo "  $(GREEN)shell$(RESET)             Open shell in Jupyter container"
	@echo ""
	@echo "$(YELLOW)Development:$(RESET)"
	@echo "  $(GREEN)install$(RESET)           Install dependencies locally with uv"
	@echo "  $(GREEN)test$(RESET)              Run tests"
	@echo "  $(GREEN)test-coverage$(RESET)     Run tests with coverage"
	@echo "  $(GREEN)lint$(RESET)              Run linters"
	@echo "  $(GREEN)format$(RESET)            Format code"
	@echo "  $(GREEN)type-check$(RESET)        Run type checker"
	@echo "  $(GREEN)check-env$(RESET)         Validate environment"
	@echo ""
	@echo "$(YELLOW)ML Workflow:$(RESET)"
	@echo "  $(GREEN)train$(RESET)             Run training (CPU)"
	@echo "  $(GREEN)train-gpu$(RESET)         Run training (GPU)"
	@echo "  $(GREEN)inference$(RESET)         Run inference on images"
	@echo "  $(GREEN)notebook$(RESET)          Show Jupyter Lab URL"
	@echo ""
	@echo "$(YELLOW)Examples:$(RESET)"
	@echo "  make up              # Start Jupyter Lab"
	@echo "  make train           # Train model (CPU)"
	@echo "  make train-gpu       # Train model (GPU)"
	@echo "  make test            # Run tests locally"

# =============================================================================
# Core Targets
# =============================================================================

.PHONY: up
up:
	@echo "$(BLUE)Starting Jupyter Lab ($(ENV) environment)...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile dev up -d
	@echo "$(GREEN)Jupyter Lab available at: http://localhost:8888$(RESET)"
	@make ps

.PHONY: down
down:
	@echo "$(BLUE)Stopping services...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile dev --profile train --profile train-gpu --profile inference down
	@echo "$(GREEN)Services stopped.$(RESET)"

.PHONY: logs
logs:
	@$(DOCKER_COMPOSE_CMD) logs -f

.PHONY: ps
ps:
	@$(DOCKER_COMPOSE_CMD) ps

.PHONY: build
build:
	@echo "$(BLUE)Building Docker images...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile dev build
	@echo "$(GREEN)Build completed.$(RESET)"

.PHONY: restart
restart:
	@echo "$(BLUE)Restarting services...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile dev restart
	@echo "$(GREEN)Services restarted.$(RESET)"
	@make ps

.PHONY: clean
clean:
	@echo "$(RED)WARNING: This will remove all containers, networks, and volumes!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(DOCKER_COMPOSE_CMD) --profile dev --profile train --profile train-gpu --profile inference down -v --remove-orphans; \
		echo "$(GREEN)Cleanup completed.$(RESET)"; \
	else \
		echo "$(YELLOW)Cleanup aborted.$(RESET)"; \
	fi

.PHONY: shell
shell:
	@echo "$(BLUE)Opening shell in $(SERVICE_NAME) container...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) bash || \
		$(DOCKER_COMPOSE_CMD) run --rm $(SERVICE_NAME) bash

# =============================================================================
# Development Targets (Local)
# =============================================================================

.PHONY: install
install:
	@echo "$(BLUE)Installing dependencies with uv...$(RESET)"
	@uv sync --all-extras
	@echo "$(GREEN)Dependencies installed.$(RESET)"

.PHONY: test
test:
	@echo "$(BLUE)Running tests...$(RESET)"
	@uv run pytest tests/ -v
	@echo "$(GREEN)Tests completed.$(RESET)"

.PHONY: test-coverage
test-coverage:
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	@uv run pytest tests/ \
		--cov=src/facial_keypoints \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=80
	@echo "$(GREEN)Coverage report generated in htmlcov/$(RESET)"

.PHONY: lint
lint:
	@echo "$(BLUE)Running linters...$(RESET)"
	@uv run ruff check src/ tests/
	@echo "$(GREEN)Linting completed.$(RESET)"

.PHONY: format
format:
	@echo "$(BLUE)Formatting code...$(RESET)"
	@uv run ruff format src/ tests/
	@uv run ruff check --fix src/ tests/
	@echo "$(GREEN)Formatting completed.$(RESET)"

.PHONY: type-check
type-check:
	@echo "$(BLUE)Running type checker...$(RESET)"
	@uv run mypy src/
	@echo "$(GREEN)Type checking completed.$(RESET)"

.PHONY: check-env
check-env:
	@echo "$(BLUE)Checking environment configuration...$(RESET)"
	@echo "$(GREEN)Environment:$(RESET) $(ENV)"
	@echo "$(GREEN)Config file:$(RESET) $(ENV_FILE)"
	@if [ -f "$(ENV_FILE)" ]; then \
		echo "$(GREEN)✓ Environment file exists$(RESET)"; \
		echo "$(YELLOW)Variables:$(RESET)"; \
		grep -v '^#' $(ENV_FILE) | grep -v '^$$' | sort; \
	else \
		echo "$(RED)✗ Environment file missing!$(RESET)"; \
		echo "$(YELLOW)Run: cp .env.example .env.$(ENV)$(RESET)"; \
		exit 1; \
	fi

# =============================================================================
# ML Workflow Targets
# =============================================================================

.PHONY: train
train:
	@echo "$(BLUE)Starting training (CPU)...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile train run --rm train
	@echo "$(GREEN)Training completed.$(RESET)"

.PHONY: train-gpu
train-gpu:
	@echo "$(BLUE)Starting training (GPU)...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile train-gpu run --rm train-gpu
	@echo "$(GREEN)Training completed.$(RESET)"

.PHONY: inference
inference:
	@echo "$(BLUE)Running inference...$(RESET)"
	@$(DOCKER_COMPOSE_CMD) --profile inference run --rm inference
	@echo "$(GREEN)Inference completed.$(RESET)"

.PHONY: notebook
notebook:
	@echo "$(BLUE)Jupyter Lab URL:$(RESET)"
	@echo "http://localhost:8888"

# =============================================================================
# Utility Targets
# =============================================================================

.PHONY: init-env
init-env:
	@if [ ! -f ".env.$(ENV)" ]; then \
		echo "$(BLUE)Creating .env.$(ENV) from example...$(RESET)"; \
		cp .env.example .env.$(ENV); \
		echo "$(YELLOW)Please edit .env.$(ENV) with your configuration$(RESET)"; \
	else \
		echo "$(GREEN).env.$(ENV) already exists$(RESET)"; \
	fi

.PHONY: lint-notebook
lint-notebook:
	@echo "$(BLUE)Linting notebooks...$(RESET)"
	@uv run nbqa ruff notebooks/
	@echo "$(GREEN)Notebook linting completed.$(RESET)"

.PHONY: format-notebook
format-notebook:
	@echo "$(BLUE)Formatting notebooks...$(RESET)"
	@uv run nbqa ruff --fix notebooks/
	@echo "$(GREEN)Notebook formatting completed.$(RESET)"
