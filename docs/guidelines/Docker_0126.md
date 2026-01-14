# Docker and Container Guidelines

**Document Version:** 2.0
**Created:** October 25, 2025
**Last Updated:** January 6, 2026
**Status:** Active Standard

## Table of Contents

1. [Overview](#overview)
2. [Dockerfile Best Practices](#dockerfile-best-practices)
3. [Docker Compose Standards](#docker-compose-standards)
4. [Multi-Stage Builds](#multi-stage-builds)
5. [Environment Configuration](#environment-configuration)
6. [Volume Management](#volume-management)
7. [Networking](#networking)
8. [Security Best Practices](#security-best-practices)
9. [Performance Optimization](#performance-optimization)
10. [CI/CD Integration](#cicd-integration)

---

## Overview

This document establishes Docker and containerization standards for all services. Consistent container practices ensure reproducible builds, secure deployments, and efficient resource usage.

**Key Principles:**

- **Reproducible Builds:** Same Dockerfile produces identical images
- **Minimal Image Size:** Use multi-stage builds and slim base images
- **Security First:** Non-root users, minimal attack surface
- **Layer Optimization:** Minimize layers and maximize cache hits
- **12-Factor App:** Environment-based configuration

**Key Technologies (2025/2026):**

- Docker BuildKit (default)
- Docker Compose v2 (compose.yaml)
- Trivy for vulnerability scanning
- Multi-stage builds

---

## Dockerfile Best Practices

### Base Image Selection

**Python Services (FastAPI, Backend):**

```dockerfile
# Use official Python slim image with specific version
FROM python:3.12-slim AS base

# For new projects, consider Python 3.13
FROM python:3.13-slim AS base
```

**Node.js Services (React, Frontend):**

```dockerfile
# Use official Node.js Alpine image
FROM node:22-alpine AS base

# For production, use specific version tags
FROM node:22.11.0-alpine AS base
```

### Standard Python Dockerfile Structure

**Dockerfile (Python/FastAPI Service):**

```dockerfile
# syntax=docker/dockerfile:1.9

# --- Stage 1: Base ---
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# --- Stage 2: Dependencies ---
FROM base AS dependencies

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- Stage 3: Development ---
FROM dependencies AS development

# Install all dependencies (including dev)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Run as non-root user
USER appuser

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Stage 4: Production ---
FROM base AS production

# Copy uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/

# Switch to non-root user
USER appuser

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application with production settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Standard Node.js Dockerfile Structure

**Dockerfile (React/Node.js Service):**

```dockerfile
# syntax=docker/dockerfile:1.9

# --- Stage 1: Base ---
FROM node:22-alpine AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# --- Stage 2: Dependencies ---
FROM base AS dependencies

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production && \
    npm cache clean --force

# --- Stage 3: Build ---
FROM base AS build

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including dev)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# --- Stage 4: Production ---
FROM node:22-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser

# Copy production dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copy built application
COPY --from=build --chown=appuser:appuser /app/dist ./dist

# Copy package.json for metadata
COPY --chown=appuser:appuser package.json ./

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Run application
CMD ["node", "dist/main.js"]
```

### Dockerfile Best Practices Checklist

**MUST:**

- [ ] Use specific version tags for base images (not `latest`)
- [ ] Use multi-stage builds to reduce image size
- [ ] Run as non-root user
- [ ] Set `PYTHONUNBUFFERED=1` for Python services
- [ ] Use `.dockerignore` file
- [ ] Include health check
- [ ] Minimize layers (combine RUN commands with `&&`)
- [ ] Clean up package manager caches
- [ ] Copy only necessary files
- [ ] Document EXPOSE ports

**SHOULD:**

- [ ] Use BuildKit syntax (`# syntax=docker/dockerfile:1.9`)
- [ ] Order layers from least to most frequently changing
- [ ] Use `COPY --chown` to set ownership in one step
- [ ] Pin dependency versions for reproducibility
- [ ] Use cache mounts for package managers
- [ ] Include metadata labels

### .dockerignore File

**REQUIRED .dockerignore:**

```
# Git
.git
.gitignore
.gitattributes

# CI/CD
.gitlab-ci.yml
.github
.circleci

# Documentation
*.md
docs/
README.md

# Tests
tests/
*.test.js
*.spec.ts
coverage/
htmlcov/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
.venv/
venv/

# Node.js
node_modules/
npm-debug.log*

# Environment
.env
.env.*
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
*.log

# Docker
Dockerfile*
docker-compose*.yml
.docker/
```

---

## Docker Compose Standards

### Standard Docker Compose Structure

**compose.yaml (Multi-Service Application):**

```yaml
name: myproject

services:
  # API Service
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: myproject/api:${VERSION:-latest}
    container_name: ${PROJECT_NAME:-myproject}-api-${ENV:-dev}
    restart: unless-stopped
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    env_file:
      - .env.${ENV:-dev}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    profiles:
      - dev
      - prod

  # Database Service
  db:
    image: postgres:16-alpine
    container_name: ${PROJECT_NAME:-myproject}-db-${ENV:-dev}
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - PGDATA=/var/lib/postgresql/data/pgdata
    env_file:
      - .env.${ENV:-dev}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    profiles:
      - dev
      - prod

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME:-myproject}-redis-${ENV:-dev}
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis-data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    profiles:
      - dev
      - prod

  # Vector Database
  qdrant:
    image: qdrant/qdrant:v1.12.0
    container_name: ${PROJECT_NAME:-myproject}-qdrant-${ENV:-dev}
    restart: unless-stopped
    ports:
      - "${QDRANT_PORT:-6333}:6333"
      - "${QDRANT_GRPC_PORT:-6334}:6334"
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    profiles:
      - dev
      - prod

networks:
  backend:
    name: ${PROJECT_NAME:-myproject}-${ENV:-dev}
    driver: bridge

volumes:
  postgres-data:
    name: ${PROJECT_NAME:-myproject}-postgres-${ENV:-dev}
  redis-data:
    name: ${PROJECT_NAME:-myproject}-redis-${ENV:-dev}
  qdrant-data:
    name: ${PROJECT_NAME:-myproject}-qdrant-${ENV:-dev}
```

### Docker Compose Best Practices

**MUST:**

- [ ] Use Compose file format version 3.8+ (or just use `name:` for v2)
- [ ] Define health checks for all services
- [ ] Use named volumes for persistent data
- [ ] Use custom networks
- [ ] Set restart policies (`unless-stopped` for services)
- [ ] Use environment variables for configuration
- [ ] Define depends_on with conditions
- [ ] Use profiles for multi-environment support

**SHOULD:**

- [ ] Use container names with environment suffix
- [ ] Expose ports via environment variables
- [ ] Use read-only mounts where applicable (`:ro`)
- [ ] Define resource limits for production

### Development Override

**compose.override.yaml (Development):**

```yaml
services:
  api:
    build:
      target: development
    volumes:
      # Mount source code for hot-reload
      - ./src:/app/src:ro
    environment:
      - DEBUG=true
      - RELOAD=true
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    ports:
      # Expose DB port for local access
      - "5432:5432"
```

### Production Override

**compose.prod.yaml (Production):**

```yaml
services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 4G
```

---

## Multi-Stage Builds

### Benefits of Multi-Stage Builds

- **Reduced Image Size:** Final image contains only runtime dependencies
- **Build Caching:** Intermediate stages cached for faster rebuilds
- **Security:** Build tools not included in production image
- **Separation of Concerns:** Clear stages for dependencies, build, and runtime

### Multi-Stage Build Pattern

```dockerfile
# --- Stage 1: Base ---
FROM python:3.12-slim AS base
# Common setup for all stages

# --- Stage 2: Dependencies ---
FROM base AS dependencies
# Install production dependencies only

# --- Stage 3: Development ---
FROM dependencies AS development
# Install all dependencies (including dev)
# Mount source code as volume

# --- Stage 4: Build ---
FROM dependencies AS build
# Compile/build application if needed

# --- Stage 5: Production ---
FROM base AS production
# Copy only production artifacts
# Minimal runtime image
```

### Building Specific Stages

```bash
# Build development image
docker build --target development -t myapp:dev .

# Build production image
docker build --target production -t myapp:prod .

# Build with cache from registry
docker build --cache-from myapp:latest --target production -t myapp:1.2.3 .
```

---

## Environment Configuration

### Environment File Structure

**REQUIRED Files:**

- `.env.dev` - Development environment
- `.env.test` - Test environment
- `.env.prod` - Production environment
- `.env.example` - Template (commit to repo)

**.env.example:**

```bash
# Application
APP_NAME=my-api
VERSION=1.0.0
ENV=dev
LOG_LEVEL=INFO
PROJECT_NAME=myproject

# API
API_PORT=8000
API_HOST=0.0.0.0

# Database
POSTGRES_USER=myapp
POSTGRES_PASSWORD=changeme
POSTGRES_DB=myapp_dev
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=changeme
REDIS_PORT=6379

# Qdrant
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334

# Security
SECRET_KEY=changeme-generate-secure-key
JWT_EXPIRATION_MINUTES=30

# AWS (Production)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

### Switching Environments

**Via Makefile:**

```makefile
# Start development environment
make up ENV=dev

# Start production environment
make up ENV=prod
```

**Via Command Line:**

```bash
# Development
ENV=dev docker compose --env-file .env.dev --profile dev up -d

# Production
ENV=prod docker compose --env-file .env.prod --profile prod up -d
```

---

## Volume Management

### Volume Types

**Named Volumes (Persistent Data):**

```yaml
volumes:
  postgres-data:
    name: ${PROJECT_NAME}-postgres-${ENV:-dev}
```

**Bind Mounts (Development):**

```yaml
volumes:
  - ./src:/app/src:ro # Read-only source code
  - ./logs:/app/logs # Writable logs
```

**tmpfs Mounts (Temporary Data):**

```yaml
tmpfs:
  - /tmp
  - /run
```

### Volume Best Practices

**MUST:**

- [ ] Use named volumes for all persistent data
- [ ] Include environment suffix in volume names
- [ ] Use bind mounts only in development
- [ ] Mount source code as read-only (`:ro`) when possible
- [ ] Never mount secrets as volumes (use environment variables)

**Backup Volumes:**

```bash
# Backup PostgreSQL volume
docker run --rm \
  -v myproject-postgres-prod:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-$(date +%Y%m%d-%H%M%S).tar.gz /data

# Restore PostgreSQL volume
docker run --rm \
  -v myproject-postgres-prod:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres-20260106-120000.tar.gz -C /
```

---

## Networking

### Network Types

**Bridge Network (Default):**

```yaml
networks:
  backend:
    driver: bridge
```

**Overlay Network (Swarm/Multi-Host):**

```yaml
networks:
  backend:
    driver: overlay
    attachable: true
```

### Service Communication

Services communicate using **service names** as hostnames:

```python
# In API service, connect to database
DATABASE_URL = "postgresql://user:pass@db:5432/dbname"
#                                      ^^
#                                   Service name

# Connect to Redis
REDIS_URL = "redis://redis:6379/0"
#                    ^^^^^
#                 Service name
```

### Network Isolation

**Separate Networks for Security:**

```yaml
services:
  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend # Not exposed to frontend

  nginx:
    networks:
      - frontend # Public-facing

networks:
  frontend:
  backend:
    internal: true # Not accessible from host
```

---

## Security Best Practices

### Run as Non-Root User

**Dockerfile:**

```dockerfile
# Create user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set ownership
COPY --chown=appuser:appuser . /app

# Switch to non-root
USER appuser
```

### Scan Images for Vulnerabilities

**Using Trivy:**

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image myapp:latest

# Fail on high/critical vulnerabilities
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest

# Scan with SBOM output
trivy image --format spdx-json myapp:latest > sbom.json
```

**Makefile Target:**

```makefile
.PHONY: scan
scan:
 @echo "$(BLUE)Scanning Docker image for vulnerabilities...$(RESET)"
 trivy image --severity HIGH,CRITICAL $(IMAGE_NAME):$(IMAGE_TAG)
```

### Secrets Management

**NEVER:**

- Hardcode secrets in Dockerfile
- Commit `.env` files with real secrets
- Log secrets

**DO:**

- Use environment variables
- Use Docker secrets (Swarm) or Kubernetes secrets
- Use external secret managers (AWS Secrets Manager, HashiCorp Vault)

**Docker BuildKit Secrets:**

```dockerfile
# syntax=docker/dockerfile:1.9

# Use secret during build (not persisted in image)
RUN --mount=type=secret,id=aws,target=/root/.aws/credentials \
    aws s3 cp s3://bucket/file.txt /app/
```

```bash
# Build with secret
docker build --secret id=aws,src=$HOME/.aws/credentials .
```

### Resource Limits

**compose.yaml:**

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M
```

---

## Performance Optimization

### Build Cache Optimization

**Order Layers by Change Frequency:**

```dockerfile
# 1. Install system dependencies (rarely changes)
RUN apt-get update && apt-get install -y curl

# 2. Copy dependency files (changes occasionally)
COPY pyproject.toml uv.lock ./

# 3. Install dependencies (changes occasionally)
RUN uv sync --frozen

# 4. Copy application code (changes frequently)
COPY src/ /app/src/
```

### Use BuildKit

**Enable BuildKit (default in Docker 23+):**

```bash
# Environment variable (for older Docker versions)
export DOCKER_BUILDKIT=1

# Or use docker buildx
docker buildx build --target production -t myapp:latest .
```

**BuildKit Features:**

```dockerfile
# syntax=docker/dockerfile:1.9

# Use cache mounts for package managers
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Use cache mounts for uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Use secret mounts (not persisted in image)
RUN --mount=type=secret,id=aws,target=/root/.aws/credentials \
    aws s3 cp s3://bucket/file.txt /app/
```

### Minimize Layers

**Bad (Many Layers):**

```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*
```

**Good (Single Layer):**

```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
```

---

## CI/CD Integration

### GitHub Actions Docker Build

**.github/workflows/docker.yml:**

```yaml
name: Docker Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix=
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          target: production
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "HIGH,CRITICAL"

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "trivy-results.sarif"
```

---

## Summary Checklist

**Every repository MUST:**

### Dockerfile

- [ ] Use multi-stage builds
- [ ] Use specific version tags for base images
- [ ] Run as non-root user
- [ ] Include health check
- [ ] Have `.dockerignore` file
- [ ] Minimize layers
- [ ] Clean up package manager caches

### Docker Compose

- [ ] Use named volumes for persistent data
- [ ] Use custom networks
- [ ] Support multiple environments (dev/test/prod)
- [ ] Use environment variables for configuration
- [ ] Define health checks for all services
- [ ] Define resource limits for production

### Security

- [ ] Scan images for vulnerabilities
- [ ] Never commit secrets
- [ ] Use non-root user
- [ ] Keep base images updated
- [ ] Implement resource limits

### CI/CD

- [ ] Build images in CI pipeline
- [ ] Run tests in containers
- [ ] Scan for vulnerabilities
- [ ] Push to container registry
- [ ] Tag images with commit SHA and version

---

**Document maintained by:** Engineering Team
**Questions/Issues:** Open issue in respective repository or documentation repo
