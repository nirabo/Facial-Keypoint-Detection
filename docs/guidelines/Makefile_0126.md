# Makefile Best Practices

**Document Version:** 2.0
**Created:** October 25, 2025
**Last Updated:** January 6, 2026
**Status:** Active Standard

## Table of Contents

- [Overview](#overview)
- [Standard Structure](#standard-structure)
- [Required Targets](#required-targets)
- [Environment Management](#environment-management)
- [Service-Specific Patterns](#service-specific-patterns)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

All repositories **MUST** include a Makefile that follows these conventions. The Makefile serves as the primary interface for developers to interact with the project, providing consistent commands across all repositories.

### Goals

1. **Consistency** - Same commands work across all repositories
2. **Discoverability** - `make help` shows all available commands
3. **Environment Safety** - Clear separation between dev/prod environments
4. **Docker Integration** - Seamless Docker Compose orchestration
5. **Developer Experience** - Simple, memorable commands

## Standard Structure

### Makefile Template

```makefile
# Project Makefile
# Description of what this repository does

# Default environment
ENV ?= dev

# Project configuration
PROJECT_NAME ?= myproject

# Docker compose configuration
COMPOSE_FILE = compose.yaml
ENV_FILE = .env.$(ENV)

# Docker compose command
DOCKER_COMPOSE_CMD = docker compose --env-file $(ENV_FILE) --profile $(ENV)

# Colors for output
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

# Required targets below...
```

## Required Targets

### Essential Targets (MUST HAVE)

All Makefiles **MUST** implement these targets:

#### 1. `help` (Default Target)

```makefile
.PHONY: help
help:
 @echo "$(BLUE)[$(PROJECT_NAME)]$(RESET) - Build System"
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
 @echo "  $(GREEN)up$(RESET)                Start all services"
 @echo "  $(GREEN)down$(RESET)              Stop and remove all services"
 @echo "  $(GREEN)restart$(RESET)           Restart all services"
 @echo "  $(GREEN)logs$(RESET)              View logs from all services"
 @echo "  $(GREEN)ps$(RESET)                List running services"
 @echo "  $(GREEN)build$(RESET)             Build or rebuild services"
 @echo "  $(GREEN)clean$(RESET)             Remove all containers and volumes"
 @echo "  $(GREEN)shell$(RESET)             Open shell in primary container"
 @echo ""
 @echo "$(YELLOW)Development:$(RESET)"
 @echo "  $(GREEN)test$(RESET)              Run tests"
 @echo "  $(GREEN)lint$(RESET)              Run linters"
 @echo "  $(GREEN)format$(RESET)            Format code"
 @echo "  $(GREEN)check-env$(RESET)         Validate environment configuration"
 @echo ""
 @echo "$(YELLOW)Examples:$(RESET)"
 @echo "  make up              # Start development environment"
 @echo "  make ENV=prod up     # Start production environment"
 @echo "  make test            # Run tests"
```

**Requirements:**

- MUST be the default target (`.DEFAULT_GOAL := help`)
- MUST show all available commands grouped by category
- MUST include usage examples
- MUST use colored output for readability

#### 2. `up` - Start Services

```makefile
.PHONY: up
up:
 @echo "$(BLUE)Starting services ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) up -d
 @echo "$(GREEN)Services started successfully.$(RESET)"
 @make ps
```

**Requirements:**

- MUST start services in detached mode (`-d`)
- MUST show running services after startup
- MUST respect ENV variable

#### 3. `down` - Stop Services

```makefile
.PHONY: down
down:
 @echo "$(BLUE)Stopping services ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) down
 @echo "$(GREEN)Services stopped successfully.$(RESET)"
```

#### 4. `logs` - View Logs

```makefile
.PHONY: logs
logs:
 @echo "$(BLUE)Viewing logs ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) logs -f
```

**Optional:** Support SERVICE parameter:

```makefile
logs:
 @if [ -z "$(SERVICE)" ]; then \
  $(DOCKER_COMPOSE_CMD) logs -f; \
 else \
  $(DOCKER_COMPOSE_CMD) logs -f $(SERVICE); \
 fi
```

#### 5. `ps` - List Services

```makefile
.PHONY: ps
ps:
 @echo "$(BLUE)Listing services ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) ps
```

#### 6. `build` - Build Services

```makefile
.PHONY: build
build:
 @echo "$(BLUE)Building services ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) build
 @echo "$(GREEN)Build completed successfully.$(RESET)"
```

#### 7. `restart` - Restart Services

```makefile
.PHONY: restart
restart:
 @echo "$(BLUE)Restarting services ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) restart
 @echo "$(GREEN)Services restarted successfully.$(RESET)"
 @make ps
```

#### 8. `clean` - Clean Up

```makefile
.PHONY: clean
clean:
 @echo "$(RED)WARNING: This will remove all containers, networks, and volumes!$(RESET)"
 @read -p "Are you sure? [y/N] " confirm; \
 if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
  $(DOCKER_COMPOSE_CMD) down -v --remove-orphans; \
  echo "$(GREEN)Cleanup completed.$(RESET)"; \
 else \
  echo "$(YELLOW)Cleanup aborted.$(RESET)"; \
 fi
```

**Requirements:**

- MUST show warning before deletion
- MUST require confirmation
- MUST use `-v` to remove volumes
- MUST use `--remove-orphans`

#### 9. `shell` - Open Shell

```makefile
.PHONY: shell
shell:
 @echo "$(BLUE)Opening shell ($(ENV) environment)...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api bash || \
  $(DOCKER_COMPOSE_CMD) run --rm api bash
```

Replace `api` with your primary service name.

#### 10. `test` - Run Tests

```makefile
.PHONY: test
test:
 @echo "$(BLUE)Running tests...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run pytest -v
 @echo "$(GREEN)Tests completed.$(RESET)"
```

#### 11. `lint` - Run Linters

```makefile
.PHONY: lint
lint:
 @echo "$(BLUE)Running linters...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run ruff check src/ tests/
 @$(DOCKER_COMPOSE_CMD) exec api uv run mypy src/
 @echo "$(GREEN)Linting completed.$(RESET)"
```

#### 12. `format` - Format Code

```makefile
.PHONY: format
format:
 @echo "$(BLUE)Formatting code...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run ruff format src/ tests/
 @echo "$(GREEN)Formatting completed.$(RESET)"
```

#### 13. `check-env` - Validate Environment

```makefile
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
  exit 1; \
 fi
```

### Recommended Targets (SHOULD HAVE)

These targets are recommended for specific service types:

#### Backend Services (Python/FastAPI)

```makefile
# Database migrations
.PHONY: migrate
migrate:
 @echo "$(BLUE)Running database migrations...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run alembic upgrade head

.PHONY: create-migration
create-migration:
 @if [ -z "$(NAME)" ]; then \
  echo "$(RED)Error: NAME required$(RESET)"; \
  echo "Usage: make create-migration NAME=description"; \
  exit 1; \
 fi
 @$(DOCKER_COMPOSE_CMD) exec api uv run alembic revision --autogenerate -m "$(NAME)"

# Type checking
.PHONY: type-check
type-check:
 @echo "$(BLUE)Running type checker...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run mypy src/

# Test coverage
.PHONY: test-coverage
test-coverage:
 @echo "$(BLUE)Running tests with coverage...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=80

# Security scanning
.PHONY: security-check
security-check:
 @echo "$(BLUE)Running security checks...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) exec api uv run bandit -r src/ -ll
 @$(DOCKER_COMPOSE_CMD) exec api uv run pip-audit
```

#### Frontend Services (React/Vite)

```makefile
# Development server
.PHONY: dev
dev:
 @echo "$(BLUE)Starting development server...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) up dev -d --build
 @echo "$(GREEN)Dev server running at http://localhost:5173$(RESET)"

# Production build
.PHONY: build-prod
build-prod:
 @echo "$(BLUE)Building production assets...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) run --rm app npm run build

# Install dependencies
.PHONY: install
install:
 @echo "$(BLUE)Installing dependencies...$(RESET)"
 @npm install

# Port cleanup (if port blocked)
.PHONY: kill-port
kill-port:
 @PORT=${PORT:-5173}; \
 echo "$(BLUE)Killing process on port $$PORT...$(RESET)"; \
 lsof -ti:$$PORT | xargs kill -9 2>/dev/null || echo "Port $$PORT is free"
```

## Environment Management

### Environment Files

Each repository **MUST** support multiple environments:

```
.env.dev          # Development configuration
.env.prod         # Production configuration
.env.test         # Test configuration (optional)
.env.example      # Template (checked into git)
```

### Environment Switching

```makefile
# Default environment
ENV ?= dev

# Validate environment
VALID_ENVS := dev prod test
ifeq ($(filter $(ENV),$(VALID_ENVS)),)
$(error Invalid environment: $(ENV). Valid: $(VALID_ENVS))
endif

# Environment-specific targets
.PHONY: init-env
init-env:
 @if [ ! -f ".env.$(ENV)" ]; then \
  echo "$(BLUE)Creating .env.$(ENV) from example...$(RESET)"; \
  cp .env.example .env.$(ENV); \
  echo "$(YELLOW)Please edit .env.$(ENV) with your configuration$(RESET)"; \
 else \
  echo "$(GREEN).env.$(ENV) already exists$(RESET)"; \
 fi
```

### Usage

```bash
make up                # Uses .env.dev (default)
make ENV=prod up       # Uses .env.prod
make ENV=test test     # Uses .env.test
```

## Service-Specific Patterns

### Pattern 1: Python Backend Service (FastAPI)

```makefile
# Primary service
SERVICE_NAME = api

# Python-specific targets
.PHONY: shell
shell:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) bash

.PHONY: python-shell
python-shell:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) python

.PHONY: test
test:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run pytest -v --cov=src

.PHONY: test-watch
test-watch:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run pytest-watch

.PHONY: lint
lint:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run ruff check src/ tests/
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run mypy src/

.PHONY: format
format:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run ruff format src/ tests/
```

### Pattern 2: Frontend Service (React/Vite)

```makefile
# Primary service
SERVICE_NAME = dev

# Frontend-specific targets
.PHONY: dev
dev:
 @docker compose up $(SERVICE_NAME) -d --build
 @echo "Dev server: http://localhost:5173"

.PHONY: install
install:
 @npm install

.PHONY: lint
lint:
 @npm run lint

.PHONY: format
format:
 @npm run format

.PHONY: type-check
type-check:
 @npm run type-check

.PHONY: build-local
build-local:
 @npm run build

.PHONY: preview
preview:
 @npm run build && npm run preview
```

## Best Practices

### 1. Use `.PHONY` for All Targets

```makefile
.PHONY: help up down logs ps build restart clean shell test lint format
```

**Why:** Prevents conflicts with files of the same name

### 2. Use Colors for Output

```makefile
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
RESET := \033[0m

# Usage
@echo "$(BLUE)Starting...$(RESET)"
@echo "$(GREEN)Success!$(RESET)"
@echo "$(YELLOW)Warning$(RESET)"
@echo "$(RED)Error!$(RESET)"
```

### 3. Suppress Command Echo with `@`

```makefile
# Good - Silent
@echo "Building..."
@docker compose build

# Bad - Shows command
echo "Building..."
docker compose build
```

### 4. Check Prerequisites

```makefile
# Check if environment file exists
ifeq (,$(wildcard $(ENV_FILE)))
$(error Environment file $(ENV_FILE) not found. Run 'make init-env' first.)
endif

# Check if Docker is running
.PHONY: check-docker
check-docker:
 @docker info > /dev/null 2>&1 || \
  (echo "$(RED)Docker is not running$(RESET)"; exit 1)
```

### 5. Provide Usage Examples

Always include examples in help:

```makefile
@echo "$(YELLOW)Examples:$(RESET)"
@echo "  make up              # Start development"
@echo "  make ENV=prod up     # Start production"
@echo "  make logs SERVICE=api # View API logs"
```

### 6. Fail Fast with Validation

```makefile
.PHONY: validate
validate:
 @echo "$(BLUE)Validating configuration...$(RESET)"
 @command -v docker >/dev/null 2>&1 || \
  (echo "$(RED)Docker not installed$(RESET)"; exit 1)
 @test -f $(ENV_FILE) || \
  (echo "$(RED)$(ENV_FILE) not found$(RESET)"; exit 1)
 @echo "$(GREEN)✓ Validation passed$(RESET)"
```

### 7. Use Confirmation for Destructive Actions

```makefile
.PHONY: clean reset drop-db
clean reset drop-db:
 @echo "$(RED)WARNING: Destructive action!$(RESET)"
 @read -p "Continue? [y/N] " confirm; \
 [ "$$confirm" = "y" ] || (echo "Aborted"; exit 1)
```

### 8. Group Related Targets

```makefile
# Development workflow
.PHONY: dev-setup dev-start dev-stop dev-reset
dev-setup: init-env build migrate
dev-start: up logs
dev-stop: down
dev-reset: clean dev-setup dev-start
```

### 9. Document Variables

```makefile
# Configuration
ENV ?= dev                    # Environment (dev, prod, test)
SERVICE_NAME ?= api           # Primary service name
DOCKER_COMPOSE_CMD ?= docker compose
```

### 10. Use Fallback Commands

```makefile
# Try exec first, fallback to run if service not running
.PHONY: shell
shell:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) bash || \
  $(DOCKER_COMPOSE_CMD) run --rm $(SERVICE_NAME) bash
```

## Examples

### Complete Python Backend Makefile

```makefile
# API Service Makefile
# FastAPI backend service

# Configuration
ENV ?= dev
PROJECT_NAME ?= myproject
SERVICE_NAME = api

# Docker compose
COMPOSE_FILE = compose.yaml
ENV_FILE = .env.$(ENV)
DOCKER_COMPOSE_CMD = docker compose --env-file $(ENV_FILE) --profile $(ENV)

# Colors
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
RESET := \033[0m

.DEFAULT_GOAL := help

.PHONY: help
help:
 @echo "$(BLUE)[$(PROJECT_NAME)]$(RESET) - API Service"
 @echo ""
 @echo "$(YELLOW)Usage:$(RESET)"
 @echo "  make [target] [ENV=dev|prod]"
 @echo ""
 @echo "$(YELLOW)Core:$(RESET)"
 @echo "  $(GREEN)up$(RESET)           Start services"
 @echo "  $(GREEN)down$(RESET)         Stop services"
 @echo "  $(GREEN)logs$(RESET)         View logs"
 @echo "  $(GREEN)shell$(RESET)        Open shell"
 @echo ""
 @echo "$(YELLOW)Development:$(RESET)"
 @echo "  $(GREEN)test$(RESET)         Run tests"
 @echo "  $(GREEN)lint$(RESET)         Run linters"
 @echo "  $(GREEN)format$(RESET)       Format code"
 @echo "  $(GREEN)migrate$(RESET)      Run migrations"
 @echo ""

.PHONY: up down logs ps build restart clean shell
up:
 @echo "$(BLUE)Starting services...$(RESET)"
 @$(DOCKER_COMPOSE_CMD) up -d
 @make ps

down:
 @$(DOCKER_COMPOSE_CMD) down

logs:
 @$(DOCKER_COMPOSE_CMD) logs -f

ps:
 @$(DOCKER_COMPOSE_CMD) ps

build:
 @$(DOCKER_COMPOSE_CMD) build

restart:
 @$(DOCKER_COMPOSE_CMD) restart
 @make ps

clean:
 @echo "$(RED)WARNING: This will remove all data!$(RESET)"
 @read -p "Continue? [y/N] " c; [ "$$c" = "y" ] && \
  $(DOCKER_COMPOSE_CMD) down -v --remove-orphans

shell:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) bash

.PHONY: test lint format type-check test-coverage
test:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run pytest -v

lint:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run ruff check src/ tests/

format:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run ruff format src/ tests/

type-check:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run mypy src/

test-coverage:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run pytest \
  --cov=src --cov-report=term-missing --cov-fail-under=80

.PHONY: migrate create-migration
migrate:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run alembic upgrade head

create-migration:
 @$(DOCKER_COMPOSE_CMD) exec $(SERVICE_NAME) uv run alembic revision --autogenerate -m "$(NAME)"
```

## Checklist for New Services

When creating a Makefile for a new service:

- [ ] Default target is `help`
- [ ] Colored output for all messages
- [ ] Multi-environment support (ENV variable)
- [ ] All required targets implemented (up, down, logs, ps, build, restart, clean, shell, test, lint, format, check-env)
- [ ] `.PHONY` declarations for all targets
- [ ] Error handling for missing environment files
- [ ] Confirmation prompts for destructive actions
- [ ] Usage examples in help text
- [ ] Consistent naming with other services
- [ ] Service-specific targets where applicable
- [ ] Documentation in comments

## Integration with CI/CD

Makefiles can be used in CI/CD pipelines:

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: make build
      - name: Test
        run: make test
      - name: Lint
        run: make lint
```

---

**Document maintained by:** Engineering Team
**Last Updated:** January 6, 2026
