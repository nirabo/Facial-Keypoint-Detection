# Testing Guidelines

**Document Version:** 2.0
**Created:** October 25, 2025
**Last Updated:** January 6, 2026
**Status:** Active Standard

## Table of Contents

1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Types and Coverage](#test-types-and-coverage)
4. [Python Testing Standards (pytest)](#python-testing-standards-pytest)
5. [JavaScript/TypeScript Testing Standards](#javascripttypescript-testing-standards)
6. [Test Organization](#test-organization)
7. [Mocking and Fixtures](#mocking-and-fixtures)
8. [CI/CD Integration](#cicd-integration)
9. [Performance Testing](#performance-testing)
10. [Security Testing](#security-testing)

---

## Overview

This document defines the testing requirements and best practices for all repositories. Consistent testing practices ensure code quality, prevent regressions, and enable confident deployments.

**Key Principles:**

- **Test Coverage:** Minimum 80% coverage for all production code
- **Test Pyramid:** More unit tests, fewer integration tests, minimal E2E tests
- **Fast Feedback:** Unit tests complete in <5s, full test suite in <5min
- **Isolation:** Tests must be independent and idempotent
- **Clarity:** Tests serve as documentation for expected behavior

**Key Technologies (2025/2026):**

- **pytest** 8.3+ for Python testing
- **pytest-asyncio** 0.24+ for async tests
- **Vitest** 2.0+ for JavaScript/TypeScript
- **Playwright** 1.50+ for E2E testing

---

## Testing Philosophy

### Test-Driven Development (TDD)

While not strictly required, TDD is **strongly encouraged** for:

- New feature development
- Bug fixes (write failing test first)
- API endpoint development
- Complex business logic

### Test Pyramid

```
           /\
          /  \
         / E2E \     ← Minimal (5%)
        /--------\
       /          \
      / Integration \  ← Moderate (25%)
     /--------------\
    /                \
   /   Unit Tests     \  ← Majority (70%)
  /--------------------\
```

**Distribution Guidelines:**

- **70% Unit Tests:** Fast, isolated, test single functions/methods
- **25% Integration Tests:** Test component interactions (API + DB, Service + Cache)
- **5% E2E Tests:** Critical user journeys only

---

## Test Types and Coverage

### Coverage Requirements

**MUST HAVE:**

- **Minimum 80% overall coverage** for production code
- **Minimum 90% coverage** for critical paths (authentication, billing, data processing)
- **100% coverage** for security-related code

**Coverage Reports:**

```bash
# Generate coverage report
make test-coverage

# View HTML report
make coverage-report
```

### Unit Tests

**Definition:** Tests that verify a single unit of code (function, method, class) in isolation.

**Requirements:**

- MUST run in <5 seconds total
- MUST NOT access external resources (databases, APIs, file system)
- MUST use mocks/stubs for dependencies
- MUST be deterministic (same input = same output)

**Example (pytest):**

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock, AsyncMock

from app.services.user_service import UserService
from app.models.user import User


class TestUserService:
    """Unit tests for UserService."""

    @pytest.fixture
    def mock_db(self) -> Mock:
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db: Mock) -> UserService:
        """Create service with mock dependencies."""
        return UserService(db=mock_db)

    async def test_create_user_success(self, service: UserService, mock_db: Mock) -> None:
        """Test successful user creation."""
        # Arrange
        user_data = {"email": "test@example.com", "name": "Test User"}

        # Act
        result = await service.create_user(user_data)

        # Assert
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    async def test_create_user_duplicate_email(
        self,
        service: UserService,
        mock_db: Mock,
    ) -> None:
        """Test user creation with duplicate email raises error."""
        # Arrange
        mock_db.execute.return_value.scalar_one_or_none.return_value = Mock()

        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            await service.create_user({"email": "existing@example.com"})
```

### Integration Tests

**Definition:** Tests that verify interactions between multiple components.

**Requirements:**

- MUST run in <2 minutes total
- MAY use test database (with cleanup)
- MAY use test cache (Redis)
- MUST clean up resources after execution
- SHOULD use Docker Compose for dependencies

**Example (pytest with test DB):**

```python
# tests/integration/test_user_api.py
import pytest
from httpx import AsyncClient

from app.main import app
from app.database import get_db
from tests.conftest import get_test_db


class TestUserAPI:
    """Integration tests for User API."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test database for each test."""
        app.dependency_overrides[get_db] = get_test_db
        yield
        app.dependency_overrides.clear()

    async def test_create_and_retrieve_user(self, client: AsyncClient) -> None:
        """Test complete user lifecycle through API."""
        # Create user
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "integration@example.com",
                "name": "Integration Test",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Retrieve user
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["email"] == "integration@example.com"
```

### End-to-End (E2E) Tests

**Definition:** Tests that verify complete user workflows across the entire system.

**Requirements:**

- MUST test critical user journeys only
- MAY run in <10 minutes total
- MUST use staging/test environment
- SHOULD use Playwright for UI testing
- MUST clean up test data

**Example (Playwright for React app):**

```typescript
// tests/e2e/user-login.spec.ts
import { test, expect } from "@playwright/test";

test.describe("User Authentication Flow", () => {
  test("user can login and access dashboard", async ({ page }) => {
    // Navigate to login
    await page.goto("/login");

    // Fill credentials
    await page.fill('[data-testid="email-input"]', "test@example.com");
    await page.fill('[data-testid="password-input"]', "password123");

    // Submit form
    await page.click('[data-testid="login-button"]');

    // Verify redirect to dashboard
    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator('[data-testid="welcome-message"]')).toContainText(
      "Welcome"
    );
  });
});
```

---

## Python Testing Standards (pytest)

### Project Structure

```
repository/
├── src/
│   └── app/
│       ├── services/
│       ├── models/
│       └── api/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_services.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── e2e/
│       ├── __init__.py
│       └── test_workflows.py
└── pyproject.toml
```

### pytest Configuration

**pyproject.toml (REQUIRED):**

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Async mode - auto detect async tests
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# Coverage settings
addopts = """
    --strict-markers
    --strict-config
    -ra
    --tb=short
"""

# Markers
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests",
    "security: Security-related tests",
]
```

### Required pytest Plugins

**Install via uv:**

```toml
# pyproject.toml
[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-mock>=3.14.0",
    "pytest-xdist>=3.5.0",    # Parallel testing
    "pytest-timeout>=2.3.0",
    "pytest-env>=1.1.0",
    "httpx>=0.28.0",          # For TestClient in FastAPI
    "faker>=33.0.0",          # Test data generation
]
```

### Fixture Guidelines

**conftest.py (Shared Fixtures):**

```python
# tests/conftest.py
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create fresh database session for each test."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession):
    """Create sample user for testing."""
    from app.models.user import User

    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="hashed_password_here",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

### Parameterized Tests

Use `@pytest.mark.parametrize` for testing multiple inputs:

```python
import pytest


@pytest.mark.parametrize(
    ("email", "is_valid"),
    [
        ("valid@example.com", True),
        ("invalid.email", False),
        ("missing@domain", False),
        ("@nodomain.com", False),
        ("valid+tag@example.co.uk", True),
    ],
)
def test_email_validation(email: str, is_valid: bool) -> None:
    """Test email validation with various inputs."""
    from app.utils.validators import is_valid_email

    assert is_valid_email(email) == is_valid
```

### Async Tests

For async functions, use `pytest-asyncio`:

```python
import pytest


@pytest.mark.asyncio
async def test_async_user_creation() -> None:
    """Test async user creation."""
    from app.services.user_service import create_user_async

    user = await create_user_async({
        "email": "async@example.com",
        "name": "Async User",
    })

    assert user.email == "async@example.com"
```

---

## JavaScript/TypeScript Testing Standards

### React Component Testing (Vitest + React Testing Library)

**vite.config.ts:**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      exclude: [
        "node_modules/",
        "tests/",
        "**/*.config.{js,ts}",
        "**/dist/**",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

**Component Test Example:**

```typescript
// src/components/UserProfile.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import UserProfile from "./UserProfile";

describe("UserProfile", () => {
  it("renders user information correctly", () => {
    const user = {
      name: "John Doe",
      email: "john@example.com",
    };

    render(<UserProfile user={user} />);

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("john@example.com")).toBeInTheDocument();
  });

  it("calls onEdit when edit button is clicked", () => {
    const mockOnEdit = vi.fn();
    const user = { name: "Jane Doe", email: "jane@example.com" };

    render(<UserProfile user={user} onEdit={mockOnEdit} />);

    fireEvent.click(screen.getByRole("button", { name: /edit/i }));

    expect(mockOnEdit).toHaveBeenCalledWith(user);
  });
});
```

### Required NPM Packages

```json
{
  "devDependencies": {
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/user-event": "^14.5.0",
    "@vitest/ui": "^2.1.0",
    "vitest": "^2.1.0",
    "jsdom": "^25.0.0",
    "@playwright/test": "^1.49.0"
  }
}
```

---

## Test Organization

### Naming Conventions

**Test Files:**

- **Python:** `test_<module_name>.py` (e.g., `test_user_service.py`)
- **JavaScript/TypeScript:** `<component>.test.tsx` or `<module>.spec.ts`

**Test Functions:**

- **Python:** `test_<action>_<expected_result>` (e.g., `test_create_user_returns_user_object`)
- **JavaScript:** `it('should <expected behavior>')` (e.g., `it('should render error message when validation fails')`)

**Test Classes (Python):**

- `class Test<ClassName>:` (e.g., `class TestUserService:`)

### Test Structure (AAA Pattern)

**Arrange-Act-Assert:**

```python
async def test_user_creation() -> None:
    """Test user creation."""
    # Arrange: Set up test data and dependencies
    user_data = {"email": "test@example.com", "name": "Test"}
    service = UserService(db=mock_db)

    # Act: Execute the function being tested
    result = await service.create_user(user_data)

    # Assert: Verify the outcome
    assert result.email == "test@example.com"
    assert result.id is not None
```

### Test Documentation

**Docstrings Required:**

```python
async def test_user_authentication_with_invalid_password() -> None:
    """
    Test that user authentication fails with incorrect password.

    Verifies:
    - Authentication returns None for invalid password
    - No session is created
    - Login attempt is logged
    """
    # Test implementation
```

---

## Mocking and Fixtures

### When to Mock

**MUST Mock:**

- External API calls
- Database operations (in unit tests)
- File system operations
- Time-dependent functions (`datetime.now()`)
- Random number generation
- Email/notification services
- Payment gateways

**SHOULD NOT Mock:**

- Simple utility functions
- Data models (use real instances)
- Configuration objects

### Python Mocking (unittest.mock)

**Mock External API:**

```python
from unittest.mock import patch, Mock, AsyncMock


@patch("app.services.notification_service.httpx.AsyncClient")
async def test_send_notification(mock_client_class: Mock) -> None:
    """Test notification sending."""
    mock_client = AsyncMock()
    mock_client.post.return_value = Mock(status_code=200, json=lambda: {"success": True})
    mock_client_class.return_value.__aenter__.return_value = mock_client

    service = NotificationService()
    result = await service.send_email("test@example.com", "Subject", "Body")

    assert result is True
    mock_client.post.assert_called_once()
```

**Mock Time:**

```python
from unittest.mock import patch
from datetime import datetime, UTC


@patch("app.services.user_service.datetime")
def test_user_creation_timestamp(mock_datetime: Mock) -> None:
    """Test user creation with fixed timestamp."""
    fixed_time = datetime(2026, 1, 6, 12, 0, 0, tzinfo=UTC)
    mock_datetime.now.return_value = fixed_time

    user = create_user({"email": "test@example.com"})

    assert user.created_at == fixed_time
```

### TypeScript Mocking (Vitest)

```typescript
import { vi } from "vitest";
import * as api from "./api";

// Mock entire module
vi.mock("./api", () => ({
  fetchUser: vi.fn(),
}));

it("should fetch user data", async () => {
  const mockUser = { id: 1, name: "John" };
  vi.mocked(api.fetchUser).mockResolvedValue(mockUser);

  const result = await getUserProfile(1);

  expect(result).toEqual(mockUser);
  expect(api.fetchUser).toHaveBeenCalledWith(1);
});
```

---

## CI/CD Integration

### GitHub Actions Configuration

**.github/workflows/test.yml:**

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-python:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          uv run pytest tests/ \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          fail_ci_if_error: true

  test-frontend:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage/lcov.info
```

### Makefile Test Targets

**Required in all repositories:**

```makefile
.PHONY: test
test:
 @echo "$(BLUE)Running tests...$(RESET)"
 uv run pytest tests/ -v

.PHONY: test-unit
test-unit:
 @echo "$(BLUE)Running unit tests...$(RESET)"
 uv run pytest tests/unit/ -v -m unit

.PHONY: test-integration
test-integration:
 @echo "$(BLUE)Running integration tests...$(RESET)"
 uv run pytest tests/integration/ -v -m integration

.PHONY: test-coverage
test-coverage:
 @echo "$(BLUE)Running tests with coverage...$(RESET)"
 uv run pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=xml \
  --cov-fail-under=80

.PHONY: test-watch
test-watch:
 @echo "$(BLUE)Running tests in watch mode...$(RESET)"
 uv run pytest-watch tests/
```

---

## Performance Testing

### Load Testing (Locust)

**Install:**

```bash
uv add --dev locust
```

**locustfile.py:**

```python
from locust import HttpUser, task, between


class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_users(self) -> None:
        """Get users list (weighted 3x)."""
        self.client.get("/api/v1/users")

    @task(1)
    def create_user(self) -> None:
        """Create user (weighted 1x)."""
        self.client.post(
            "/api/v1/users",
            json={
                "email": f"load-test-{self.environment.stats.num_requests}@example.com",
                "name": "Load Test User",
                "password": "SecurePass123!",
            },
        )

    def on_start(self) -> None:
        """Login before tasks."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "admin123",
            },
        )
        self.token = response.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"
```

**Run Load Test:**

```bash
# Local
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# CI/CD
locust -f tests/performance/locustfile.py \
    --headless \
    -u 100 \
    -r 10 \
    --run-time 60s \
    --host=http://api:8000
```

---

## Security Testing

### Static Security Analysis

**Python (Bandit):**

```bash
# Install
uv add --dev bandit

# Run
uv run bandit -r src/ -f json -o bandit-report.json
```

**JavaScript (npm audit):**

```bash
npm audit --audit-level=moderate
```

### Dependency Vulnerability Scanning

**Python (pip-audit):**

```bash
uv add --dev pip-audit
uv run pip-audit
```

**Makefile Target:**

```makefile
.PHONY: security-check
security-check:
 @echo "$(BLUE)Running security checks...$(RESET)"
 uv run bandit -r src/ -ll
 uv run pip-audit
 @echo "$(GREEN)Security checks passed.$(RESET)"
```

### Authentication/Authorization Tests

**Example (FastAPI):**

```python
async def test_protected_endpoint_requires_authentication(
    client: AsyncClient,
) -> None:
    """Test that protected endpoint returns 401 without token."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_protected_endpoint_with_valid_token(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that protected endpoint works with valid token."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200


async def test_admin_endpoint_rejects_regular_user(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    """Test that admin endpoint rejects non-admin users."""
    response = await client.delete(
        "/api/v1/users/123",
        headers=user_auth_headers,
    )
    assert response.status_code == 403
```

---

## Summary Checklist

**Every repository MUST:**

- [ ] Maintain minimum 80% test coverage
- [ ] Include unit, integration, and E2E tests (70/25/5 distribution)
- [ ] Use pytest (Python) or Vitest (JavaScript/TypeScript)
- [ ] Configure coverage reporting in CI/CD
- [ ] Implement test fixtures and proper mocking
- [ ] Follow AAA (Arrange-Act-Assert) pattern
- [ ] Include test documentation (docstrings)
- [ ] Run tests on every MR/PR
- [ ] Include security testing (Bandit, npm audit)
- [ ] Provide Makefile targets: `test`, `test-coverage`, `test-unit`, `test-integration`

**Test Execution Time Limits:**

- Unit tests: <5 seconds total
- Integration tests: <2 minutes total
- E2E tests: <10 minutes total
- Full test suite (CI/CD): <5 minutes total

---

**Document maintained by:** Engineering Team
**Questions/Issues:** Open issue in respective repository or documentation repo
