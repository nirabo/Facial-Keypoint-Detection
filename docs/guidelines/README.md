# Development Guidelines

**Version:** 2.0
**Created:** October 25, 2025
**Last Updated:** January 6, 2026
**Status:** Active Standard

## Overview

This directory contains comprehensive coding guidelines and standards that ensure consistency, maintainability, security, and quality across all project repositories.

**Purpose:**

- Establish consistent coding practices across all teams
- Define required tools and workflows
- Ensure code quality and security standards
- Enable efficient collaboration and code reviews
- Maintain reproducible builds and deployments

**Scope:**

- Python backend services (FastAPI, core APIs, microservices)
- JavaScript/TypeScript frontend services (React, Vue, mobile apps)
- Infrastructure and deployment (Docker, CI/CD)
- Version control and collaboration (Git workflow)
- Testing and quality assurance

---

## Quick Start

### For New Repositories

When creating a new repository:

1. **Read all guidelines** in this directory
2. **Copy templates** from guidelines (Makefile, Dockerfile, etc.)
3. **Configure tools** according to standards (Ruff, mypy, pytest)
4. **Set up CI/CD** following GitHub Actions/GitLab CI patterns
5. **Enable branch protection** on main branch
6. **Add README** following documentation standards

### For Existing Repositories

When updating existing repositories:

1. **Audit compliance** against all guidelines
2. **Create migration plan** for non-compliant areas
3. **Update incrementally** to avoid disruption
4. **Document deviations** (if any) with justification
5. **Request review** from architecture team

---

## Guidelines Index

### 1. [Python Coding Standards](Python_0126.md)

**Topic:** Python language best practices

**Covers:**

- Python version requirements (3.12+)
- Package management (uv)
- Code style and formatting (Ruff)
- Type hints (mypy)
- Code organization (imports, modules, packages)
- Naming conventions
- Error handling (custom exceptions)
- Logging (structured logging)
- Documentation (Google-style docstrings)
- Best practices (context managers, comprehensions, async/await)
- Performance and security guidelines

**Key Requirements:**

- Python 3.12+ (recommended 3.13 for new projects)
- uv for package management
- Ruff for linting and formatting
- mypy for type checking
- Type hints for all public functions
- Google-style docstrings

---

### 2. [FastAPI Best Practices](FastAPI_0126.md)

**Topic:** FastAPI application development standards

**Covers:**

- Project structure and organization
- Code style and architecture
- API design principles (OpenAPI 3.1)
- Request/response handling (Pydantic v2)
- Authentication and authorization
- Database integration (SQLAlchemy 2.0+)
- Error handling and validation
- Performance optimization
- Testing strategies
- Security best practices

**Key Requirements:**

- FastAPI 0.115+ with Pydantic v2
- Async database drivers (asyncpg, databases)
- SQLAlchemy 2.0+ with async support
- Lifespan context managers
- Structured error responses

---

### 3. [Docker Guidelines](Docker_0126.md)

**Topic:** Containerization standards

**Covers:**

- Dockerfile best practices (BuildKit)
- Multi-stage builds
- Base image selection
- Docker Compose standards
- Environment configuration
- Volume management
- Networking (service communication)
- Security best practices (non-root users, vulnerability scanning)
- Performance optimization
- CI/CD integration

**Key Requirements:**

- Multi-stage builds (dependencies, build, production)
- Non-root user
- Health checks
- .dockerignore file
- Multi-environment Docker Compose (dev/prod)
- Vulnerability scanning (Trivy)

---

### 4. [Git Workflow](Git_0126.md)

**Topic:** Version control and collaboration

**Covers:**

- Branching strategy (feature, fix, hotfix, release)
- Branch naming conventions
- Commit message standards (Conventional Commits)
- Pull request process
- Code review guidelines
- Merge strategies (squash, rebase)
- Release management (semantic versioning)
- Hotfix process
- Best practices (.gitignore, hooks)

**Key Requirements:**

- Conventional Commits format
- Feature branches (no direct commits to main)
- Branch protection (reviews required)
- PR template
- Squash and merge (default)
- Semantic versioning

---

### 5. [Testing Standards](Testing_0126.md)

**Topic:** Testing practices and requirements

**Covers:**

- Testing philosophy (TDD encouraged)
- Test types (unit, integration, E2E)
- Coverage requirements (minimum 80%)
- Python testing (pytest, fixtures, mocking)
- JavaScript/TypeScript testing (Vitest, React Testing Library)
- Test organization and structure
- CI/CD integration
- Performance testing (Locust)
- Security testing (Bandit, npm audit)

**Key Requirements:**

- Minimum 80% overall test coverage
- Minimum 90% coverage for critical paths
- Test pyramid distribution (70% unit, 25% integration, 5% E2E)
- Tests run in CI/CD on every MR/PR

---

### 6. [Makefile Standards](Makefile_0126.md)

**Topic:** Build system and task automation

**Covers:**

- Standard Makefile structure
- Required targets (help, up, down, logs, ps, build, restart, clean, shell, test, lint, format, check-env)
- Service-specific patterns (Python backend, React frontend)
- Environment management (ENV variable, .env files)
- Docker Compose integration
- Testing and linting integration
- Best practices (colored output, .PHONY, validation, confirmation prompts)

**Key Requirements:**

- 13 required targets that every repository MUST implement
- Multi-environment support (dev/prod/test)
- Colored terminal output
- Help command as default target

---

## Compliance Matrix

### Required Tools by Repository Type

| Tool/Standard         | Python Backend | React Frontend | Edge Agents  |
| --------------------- | -------------- | -------------- | ------------ |
| **Makefile**          | Required       | Required       | Required     |
| **Docker**            | Required       | Required       | Required     |
| **Git Workflow**      | Required       | Required       | Required     |
| **Testing (80%)**     | Required       | Required       | Required     |
| **Python Standards**  | Required       | N/A            | If Python    |
| **FastAPI Standards** | Required       | N/A            | N/A          |
| **Ruff**              | Required       | N/A            | If Python    |
| **mypy**              | Required       | N/A            | If Python    |
| **pytest**            | Required       | N/A            | If Python    |
| **Vitest**            | N/A            | Required       | N/A          |
| **ESLint**            | N/A            | Required       | N/A          |

---

## Enforcement

### Required CI/CD Checks

**Every MR/PR MUST pass:**

1. **Linting**

   ```bash
   make lint
   ```

2. **Type Checking**

   ```bash
   make type-check  # Python: mypy, JS: tsc
   ```

3. **Tests**

   ```bash
   make test-coverage
   # Must achieve >80% coverage
   ```

4. **Security Scanning**

   ```bash
   make security-check  # Bandit, npm audit
   ```

5. **Docker Build**

   ```bash
   docker build --target production .
   ```

6. **Vulnerability Scanning**

   ```bash
   trivy image <image-name>
   ```

### GitHub Actions Template

**Minimal .github/workflows/ci.yml (REQUIRED):**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      - name: Lint
        run: |
          make lint
          make type-check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      - name: Test
        run: make test-coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build --target production -t app:${{ github.sha }} .

  scan:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:${{ github.sha }}
          severity: HIGH,CRITICAL
          exit-code: '1'
```

---

## Repository Checklist

### New Repository Setup

When creating a new repository, ensure:

**Repository Structure:**

- [ ] Standard directory structure (src/, tests/, docs/)
- [ ] README.md with project overview
- [ ] LICENSE file
- [ ] .gitignore (comprehensive)
- [ ] .dockerignore
- [ ] CHANGELOG.md (Keep a Changelog format)

**Development Files:**

- [ ] Makefile (following [Makefile_0126.md](Makefile_0126.md))
- [ ] Dockerfile (multi-stage, following [Docker_0126.md](Docker_0126.md))
- [ ] docker-compose.yml (multi-environment)
- [ ] .env.example (all required variables)

**Python Configuration (if applicable):**

- [ ] pyproject.toml (project metadata, dependencies, tool configs)
- [ ] uv.lock (locked dependencies)
- [ ] Ruff configuration in pyproject.toml
- [ ] mypy configuration in pyproject.toml
- [ ] pytest configuration in pyproject.toml

**JavaScript Configuration (if applicable):**

- [ ] package.json (project metadata, dependencies, scripts)
- [ ] package-lock.json (locked dependencies)
- [ ] tsconfig.json (TypeScript configuration)
- [ ] vite.config.ts or similar build config
- [ ] ESLint configuration

**Testing:**

- [ ] tests/ directory with unit/, integration/, e2e/ subdirs
- [ ] conftest.py (Python) or setup.ts (JS) with shared fixtures
- [ ] Test coverage configured
- [ ] CI/CD runs tests on every MR/PR

**CI/CD:**

- [ ] .github/workflows/ci.yml or .gitlab-ci.yml with required stages
- [ ] Branch protection rules on main
- [ ] Required approvals configured
- [ ] MR/PR template

**Documentation:**

- [ ] README.md (installation, usage, development)
- [ ] API documentation (if applicable)
- [ ] Contributing guide
- [ ] Link to this guidelines directory

---

## Deviations and Exceptions

### Requesting Deviation

If a repository **cannot** comply with a guideline:

1. **Document reason** in repository README
2. **Create issue** in documentation repository explaining deviation
3. **Get approval** from architecture team
4. **Set timeline** for compliance (if temporary)

**Example Deviation Documentation:**

```markdown
## Guideline Deviations

### Python Version

**Guideline:** Python 3.12+ required
**Current:** Python 3.11
**Reason:** Dependency on legacy library incompatible with 3.12
**Plan:** Migrate to Python 3.12 by Q2 2026
**Approved by:** @architecture-team
**Issue:** #1234
```

---

## Contributing to Guidelines

### Updating Guidelines

To propose changes to these guidelines:

1. **Open issue** in documentation repository
2. **Describe change** and rationale
3. **Create MR/PR** with proposed updates
4. **Get review** from architecture team and affected teams
5. **Document migration path** for existing repositories

### Guidelines Review Cycle

- **Quarterly review** of all guidelines
- **Version updates** when changes approved
- **Communication** to all teams when guidelines change
- **Migration support** for breaking changes

---

## Support and Questions

### Getting Help

**Questions about guidelines:**

- Open issue in documentation repository
- Tag with `guidelines` label
- Mention affected repositories

**Implementation support:**

- Reach out to architecture team
- Schedule pair programming session
- Request code review from experienced team member

**Reporting issues:**

- Document specific non-compliance issue
- Provide context and repository link
- Suggest resolution if possible

---

## Version History

### Version 2.0 (January 6, 2026)

**Updated for 2025/2026 best practices:**

- Updated Python requirements to 3.12+ (3.13 recommended)
- Updated Ruff configuration for latest version
- Added uv 0.5+ features and best practices
- Updated FastAPI to 0.115+ with Pydantic v2
- Updated Docker practices for BuildKit and multi-stage builds
- Added GitHub Actions as default CI/CD option
- Removed project-specific references (made generic)

### Version 1.0 (October 25, 2025)

**Initial release** containing:

- FastAPI best practices
- Makefile standards
- Testing standards
- Python coding standards
- Docker guidelines
- Git workflow

---

## Quick Reference

### Essential Commands

**Every repository supports these commands:**

```bash
# Get help
make help

# Start services (development)
make up

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type check
make type-check

# Stop services
make down

# View logs
make logs

# Access service shell
make shell
```

### Essential Files

**Every repository contains these files:**

```
repository/
├── README.md
├── Makefile                    # Build system
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Service orchestration
├── .env.example                # Environment template
├── .gitignore                  # Git exclusions
├── .dockerignore               # Docker exclusions
├── .github/workflows/ci.yml    # CI/CD pipeline
├── CHANGELOG.md                # Release history
├── pyproject.toml              # Python config (if applicable)
├── package.json                # Node config (if applicable)
├── src/                        # Source code
└── tests/                      # Test suite
    ├── unit/
    ├── integration/
    └── e2e/
```

---

**Document maintained by:** Engineering Team
**Last Review:** January 6, 2026
**Next Review:** April 6, 2026
