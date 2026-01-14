# Python Coding Standards

**Document Version:** 2.0
**Created:** October 25, 2025
**Last Updated:** January 6, 2026
**Status:** Active Standard

## Table of Contents

1. [Overview](#overview)
2. [Python Version](#python-version)
3. [Package Management](#package-management)
4. [Code Style and Formatting](#code-style-and-formatting)
5. [Type Hints](#type-hints)
6. [Code Organization](#code-organization)
7. [Naming Conventions](#naming-conventions)
8. [Error Handling](#error-handling)
9. [Logging](#logging)
10. [Documentation](#documentation)
11. [Best Practices](#best-practices)
12. [Performance Guidelines](#performance-guidelines)
13. [Security Guidelines](#security-guidelines)

---

## Overview

This document establishes Python coding standards for all backend services. Consistent coding practices improve code readability, maintainability, and collaboration across teams.

**Key Tools:**

- **Python 3.12+** (required minimum version, 3.13 recommended for new projects)
- **uv** for package management (0.5+)
- **Ruff** for linting and formatting (0.8+)
- **mypy** for static type checking (1.13+)
- **FastAPI** for API development

---

## Python Version

### Required Version

**MUST use Python 3.12 or higher** for all services. **Python 3.13 is recommended** for new projects.

**Python 3.12 Benefits:**

- 15% faster than 3.11
- Improved error messages with suggestions
- Per-interpreter GIL (PEP 684)
- Type parameter syntax (`class Box[T]:`)
- Better f-string debugging

**Python 3.13 Benefits (New Projects):**

- Experimental free-threaded mode (no GIL)
- Improved interactive interpreter (REPL)
- Faster startup time
- Better error messages with color support
- `typing.TypeIs` for type narrowing

**Dockerfile:**

```dockerfile
FROM python:3.12-slim AS base

# Or for new projects
FROM python:3.13-slim AS base

WORKDIR /app

# Install uv (recommended method)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Package Management

### uv (Required)

**MUST use uv** for package management. uv is a fast Python package manager written in Rust.

**Installation:**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv

# Or via Homebrew
brew install uv
```

**Project Initialization:**

```bash
# Create new project
uv init my-project
cd my-project

# Or initialize in existing directory
uv init

# Create virtual environment
uv venv

# Activate (optional, uv runs commands in venv automatically)
source .venv/bin/activate
```

**Dependency Management:**

```bash
# Add dependencies
uv add fastapi uvicorn sqlalchemy

# Add development dependencies
uv add --dev pytest pytest-cov ruff mypy

# Install from pyproject.toml
uv sync

# Install with all extras
uv sync --all-extras

# Lock dependencies
uv lock

# Update dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package fastapi
```

**pyproject.toml (Required Structure):**

```toml
[project]
name = "my-service"
version = "1.0.0"
description = "Service description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

---

## Code Style and Formatting

### Ruff Configuration

**MUST use Ruff** for linting and formatting. Ruff replaces Black, isort, flake8, and pylint.

**pyproject.toml (REQUIRED):**

```toml
[tool.ruff]
# Python version
target-version = "py312"

# Line length
line-length = 100

# Source directory
src = ["src"]

# Exclude paths
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.lint]
# Enable additional rules
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "ANN",    # flake8-annotations
    "ASYNC",  # flake8-async
    "S",      # flake8-bandit (security)
    "B",      # flake8-bugbear
    "A",      # flake8-builtins
    "C4",     # flake8-comprehensions
    "DTZ",    # flake8-datetimez
    "T10",    # flake8-debugger
    "EM",     # flake8-errmsg
    "FA",     # flake8-future-annotations
    "ISC",    # flake8-implicit-str-concat
    "ICN",    # flake8-import-conventions
    "LOG",    # flake8-logging
    "G",      # flake8-logging-format
    "PIE",    # flake8-pie
    "T20",    # flake8-print
    "PT",     # flake8-pytest-style
    "Q",      # flake8-quotes
    "RSE",    # flake8-raise
    "RET",    # flake8-return
    "SLF",    # flake8-self
    "SIM",    # flake8-simplify
    "TID",    # flake8-tidy-imports
    "TCH",    # flake8-type-checking
    "ARG",    # flake8-unused-arguments
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented-out code)
    "PL",     # pylint
    "TRY",    # tryceratops
    "FLY",    # flynt (f-string conversion)
    "PERF",   # perflint
    "FURB",   # refurb
    "RUF",    # Ruff-specific rules
]

# Ignore specific rules
ignore = [
    "ANN101",  # Missing type annotation for self
    "ANN102",  # Missing type annotation for cls
    "ANN401",  # Dynamically typed expressions (Any)
    "PLR0913", # Too many arguments
    "TRY003",  # Avoid specifying long messages outside exception class
    "ISC001",  # Conflicts with formatter
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",    # Use of assert
    "ARG",     # Unused function arguments
    "PLR2004", # Magic value used in comparison
    "ANN",     # Type annotations not required in tests
]
"alembic/**/*.py" = [
    "INP001",  # Missing __init__.py
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # Use Google docstring style

[tool.ruff.lint.isort]
known-first-party = ["app"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = true
```

**Makefile Targets:**

```makefile
.PHONY: lint
lint:
 @echo "$(BLUE)Running linter...$(RESET)"
 uv run ruff check src/ tests/

.PHONY: format
format:
 @echo "$(BLUE)Formatting code...$(RESET)"
 uv run ruff format src/ tests/
 uv run ruff check --fix src/ tests/

.PHONY: format-check
format-check:
 @echo "$(BLUE)Checking code formatting...$(RESET)"
 uv run ruff format --check src/ tests/
```

### Code Style Rules

**Line Length:**

- **MUST NOT exceed 100 characters** (enforced by Ruff)
- Use line continuation for long expressions

**Imports:**

```python
# Standard library imports first
import os
import sys
from datetime import datetime, timedelta

# Third-party imports second
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

# Local imports last
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
```

**Quotes:**

- **MUST use double quotes** for strings (`"example"`)
- Use single quotes only for strings containing double quotes

**Trailing Commas:**

- **MUST use trailing commas** in multi-line collections

```python
# Good
user_data = {
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": True,  # Trailing comma
}

# Bad
user_data = {
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": True  # No trailing comma
}
```

---

## Type Hints

### Mandatory Type Hints

**MUST use type hints for:**

- All function signatures (parameters and return types)
- Class attributes
- Module-level variables

**Exceptions:**

- `self` in instance methods (inferred)
- `cls` in class methods (inferred)
- Local variables (when type is obvious)

### mypy Configuration

**pyproject.toml (REQUIRED):**

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true
plugins = ["pydantic.mypy"]

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "alembic.*"
ignore_errors = true
```

### Type Hint Examples

**Modern Python 3.12+ Syntax:**

```python
# Use built-in generics (no need to import from typing)
def get_users(limit: int = 10) -> list[User]:
    """Get list of users."""
    ...

def get_user_by_email(email: str) -> User | None:
    """Get user by email, returns None if not found."""
    ...

def process_data(data: dict[str, int]) -> set[str]:
    """Process data dictionary."""
    ...
```

**Type Parameter Syntax (Python 3.12+):**

```python
# New generic syntax
class Repository[T]:
    """Generic repository pattern."""

    def __init__(self, model: type[T]) -> None:
        self.model = model

    def get_all(self) -> list[T]:
        """Get all records."""
        ...

    def get_by_id(self, id: int) -> T | None:
        """Get record by ID."""
        ...

# Usage
user_repo = Repository[User](User)
```

**Function with Complex Types:**

```python
from collections.abc import Callable, Coroutine
from typing import Any


def create_user(
    email: str,
    name: str,
    *,
    is_active: bool = True,
    metadata: dict[str, Any] | None = None,
) -> User:
    """
    Create a new user.

    Args:
        email: User email address
        name: User full name
        is_active: Whether user account is active
        metadata: Additional user metadata

    Returns:
        Created User instance

    Raises:
        ValueError: If email is invalid
    """
    if not is_valid_email(email):
        raise ValueError(f"Invalid email: {email}")

    return User(
        email=email,
        name=name,
        is_active=is_active,
        metadata=metadata or {},
        created_at=datetime.now(tz=UTC),
    )


# Async function with callback
async def fetch_with_retry(
    url: str,
    callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
) -> dict[str, Any]:
    """Fetch URL with retry and callback."""
    ...
```

**Protocol Types (Structural Subtyping):**

```python
from typing import Protocol


class Authenticatable(Protocol):
    """Protocol for authenticatable objects."""

    def verify_password(self, password: str) -> bool:
        """Verify password."""
        ...

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        ...


# TypeIs for type narrowing (Python 3.13+)
from typing import TypeIs


def is_valid_user(obj: object) -> TypeIs[User]:
    """Check if object is a valid User."""
    return isinstance(obj, User) and obj.is_active
```

---

## Code Organization

### Project Structure

**Standard Python Service:**

```
repository/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── config.py            # Configuration
│       ├── database.py          # Database setup
│       ├── dependencies.py      # FastAPI dependencies
│       │
│       ├── api/                 # API endpoints
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   ├── users.py
│       │   │   └── auth.py
│       │
│       ├── models/              # SQLAlchemy models
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── user.py
│       │   └── item.py
│       │
│       ├── schemas/             # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── item.py
│       │
│       ├── services/            # Business logic
│       │   ├── __init__.py
│       │   ├── user_service.py
│       │   └── auth_service.py
│       │
│       ├── repositories/        # Data access layer
│       │   ├── __init__.py
│       │   └── user_repository.py
│       │
│       ├── utils/               # Utility functions
│       │   ├── __init__.py
│       │   ├── validators.py
│       │   └── helpers.py
│       │
│       └── middleware/          # Custom middleware
│           ├── __init__.py
│           └── logging.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/                     # Database migrations
│   ├── versions/
│   └── env.py
│
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

### Module Imports

**Absolute Imports Only:**

```python
# Good
from app.services.user_service import UserService
from app.models.user import User

# Bad
from ..services.user_service import UserService
from .models.user import User
```

**Avoid Circular Imports:**

```python
# models/user.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.item import Item


class User:
    items: list["Item"]  # Forward reference
```

---

## Naming Conventions

### General Rules

- **snake_case:** Functions, variables, module names
- **PascalCase:** Classes, type aliases
- **UPPER_SNAKE_CASE:** Constants
- **\_leading_underscore:** Internal/private members

### Examples

```python
# Constants
MAX_RETRY_ATTEMPTS = 3
API_TIMEOUT_SECONDS = 30
DEFAULT_PAGE_SIZE = 20

# Classes
class UserService:
    """Service for user management."""
    pass

class HTTPException:
    """HTTP exception."""
    pass

# Functions and variables
def calculate_total_cost(items: list[Item]) -> Decimal:
    """Calculate total cost."""
    total_amount = Decimal(0)
    for item in items:
        total_amount += item.price
    return total_amount

# Private members
class User:
    def __init__(self, email: str) -> None:
        self._email = email  # Internal attribute
        self.__password_hash = ""  # Name-mangled attribute

    def _validate_email(self) -> bool:
        """Internal validation method."""
        return "@" in self._email
```

### Boolean Names

Use descriptive names that indicate true/false:

```python
# Good
is_active: bool
has_permission: bool
can_edit: bool
should_retry: bool

# Bad
active: bool
permission: bool
edit: bool
retry: bool
```

---

## Error Handling

### Exception Guidelines

**MUST use specific exceptions:**

```python
# Good
raise ValueError(f"Invalid email format: {email}")
raise KeyError(f"User not found: {user_id}")

# Bad
raise Exception("Something went wrong")
```

**Create custom exceptions:**

```python
# app/exceptions.py
class AppException(Exception):
    """Base exception for application services."""
    pass


class UserNotFoundError(AppException):
    """Raised when user is not found."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    pass


class ValidationError(AppException):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"Validation error on {field}: {message}")
```

### Try-Except Best Practices

**Catch specific exceptions:**

```python
# Good
try:
    user = get_user(user_id)
except UserNotFoundError:
    logger.warning("User %s not found", user_id)
    return None
except DatabaseError as e:
    logger.error("Database error: %s", e)
    raise

# Bad
try:
    user = get_user(user_id)
except Exception:
    return None
```

**Use exception groups (Python 3.11+):**

```python
async def process_users(user_ids: list[int]) -> list[User]:
    """Process multiple users, collecting errors."""
    results = await asyncio.gather(
        *[fetch_user(uid) for uid in user_ids],
        return_exceptions=True,
    )

    errors: list[BaseException] = []
    users: list[User] = []

    for result in results:
        if isinstance(result, BaseException):
            errors.append(result)
        else:
            users.append(result)

    if errors:
        raise ExceptionGroup("Failed to process some users", errors)

    return users


# Handling exception groups
try:
    users = await process_users([1, 2, 3])
except* UserNotFoundError as eg:
    for exc in eg.exceptions:
        logger.warning("User not found: %s", exc.user_id)
except* DatabaseError as eg:
    logger.error("Database errors: %d", len(eg.exceptions))
    raise
```

### FastAPI Exception Handlers

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import UserNotFoundError, AuthenticationError


app = FastAPI()


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError,
) -> JSONResponse:
    """Handle UserNotFoundError."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "user_not_found",
            "message": str(exc),
            "user_id": exc.user_id,
        },
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(
    request: Request,
    exc: AuthenticationError,
) -> JSONResponse:
    """Handle AuthenticationError."""
    return JSONResponse(
        status_code=401,
        content={
            "error": "authentication_failed",
            "message": "Authentication failed",
        },
    )
```

---

## Logging

### Configuration

**MUST use Python's standard logging module** configured via structlog for structured logging.

**app/config.py:**

```python
import logging
import sys
from pydantic_settings import BaseSettings
import structlog


class Settings(BaseSettings):
    """Application settings."""

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or console
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()


def setup_logging() -> None:
    """Configure application logging with structlog."""
    # Configure structlog processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
    ]

    if settings.LOG_FORMAT == "json":
        # JSON formatting for production
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    else:
        # Console formatting for development
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

    # Set log level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )
```

### Logging Best Practices

**Use module-level logger:**

```python
import structlog


logger = structlog.get_logger(__name__)


def create_user(email: str) -> User:
    """Create user."""
    logger.info("creating_user", email=email)

    try:
        user = User(email=email)
        db.add(user)
        db.commit()
        logger.info("user_created", user_id=user.id, email=email)
        return user
    except Exception as e:
        logger.error("user_creation_failed", email=email, error=str(e))
        raise
```

**Log Levels:**

- **DEBUG:** Detailed diagnostic information
- **INFO:** General informational messages (user created, request processed)
- **WARNING:** Something unexpected but handled (deprecated feature used)
- **ERROR:** Error occurred but application continues
- **CRITICAL:** Severe error, application may crash

**Structured Logging:**

```python
logger.info(
    "user_authenticated",
    user_id=user.id,
    email=user.email,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
)
```

**Avoid logging sensitive data:**

```python
# Bad
logger.info("User login: %s / %s", user.email, password)

# Good
logger.info("user_login_attempt", user_id=user.id)
```

---

## Documentation

### Docstrings (Google Style)

**MUST include docstrings for:**

- All public modules
- All public classes
- All public functions/methods

**Module Docstring:**

```python
"""
User service module.

This module provides user management functionality including creation,
authentication, and profile updates.
"""
```

**Function Docstring:**

```python
def create_user(
    email: str,
    name: str,
    *,
    password: str,
    is_active: bool = True,
) -> User:
    """
    Create a new user account.

    Creates a user with the provided details, hashes the password,
    and stores in the database.

    Args:
        email: User email address (must be unique)
        name: User full name
        password: Plain text password (will be hashed)
        is_active: Whether account is active (default: True)

    Returns:
        Created User instance with assigned ID

    Raises:
        ValueError: If email format is invalid
        DuplicateEmailError: If email already exists
        DatabaseError: If database operation fails

    Example:
        >>> user = create_user(
        ...     email="john@example.com",
        ...     name="John Doe",
        ...     password="SecurePass123!",
        ... )
        >>> user.id
        1
    """
    # Implementation
```

**Class Docstring:**

```python
class UserRepository:
    """
    Repository for user data access.

    Provides methods to query, create, update, and delete users
    from the database.

    Attributes:
        db: Database session

    Example:
        >>> repo = UserRepository(db=session)
        >>> user = repo.get_by_email("john@example.com")
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize repository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
```

---

## Best Practices

### Use Context Managers

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator


# File operations
with open("data.txt") as f:
    data = f.read()

# Async context managers
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session with automatic cleanup."""
    session = AsyncSession(engine)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# Usage
async with get_db_session() as session:
    user = await session.get(User, user_id)
```

### Use Comprehensions

```python
# List comprehension
active_users = [user for user in users if user.is_active]

# Dict comprehension
user_map = {user.id: user.name for user in users}

# Set comprehension
unique_emails = {user.email for user in users}

# Generator expression for large datasets
total = sum(item.price for item in items)
```

### Use Dataclasses for Simple Data Structures

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Video file metadata (immutable)."""

    filename: str
    duration_seconds: int
    resolution: tuple[int, int]
    codec: str
    created_at: datetime = field(default_factory=datetime.now)
```

### Use Enums for Fixed Sets

```python
from enum import StrEnum, auto


class UserRole(StrEnum):
    """User role enumeration."""

    ADMIN = auto()
    USER = auto()
    VIEWER = auto()


class ProcessingStatus(StrEnum):
    """Video processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

### Avoid Mutable Default Arguments

```python
# Bad
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

# Good
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## Performance Guidelines

### Use Async/Await for I/O Operations

```python
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# Database queries
async def get_users(db: AsyncSession) -> list[User]:
    """Get all users asynchronously."""
    result = await db.execute(select(User))
    return list(result.scalars().all())


# HTTP requests
async def fetch_data(url: str) -> dict:
    """Fetch data from external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


# Concurrent execution
async def fetch_all_data(urls: list[str]) -> list[dict]:
    """Fetch data from multiple URLs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

### Use Generators for Large Datasets

```python
from collections.abc import Iterator
import json


def process_large_file(filepath: str) -> Iterator[dict]:
    """Process large file line by line."""
    with open(filepath) as f:
        for line in f:
            yield json.loads(line)


# Usage
for record in process_large_file("large_data.jsonl"):
    process_record(record)
```

### Batch Database Operations

```python
# Bad: N+1 queries
for user_id in user_ids:
    user = await db.execute(select(User).where(User.id == user_id))
    process_user(user.scalar_one())

# Good: Single query with IN clause
result = await db.execute(select(User).where(User.id.in_(user_ids)))
for user in result.scalars().all():
    process_user(user)
```

---

## Security Guidelines

### Never Store Plain Text Passwords

```python
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### Use Environment Variables for Secrets

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_URL: str
    SECRET_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


# Never commit .env files
# Use .env.example instead
```

### Validate Input Data

```python
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """User creation schema."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v
```

---

## Summary Checklist

**Every repository MUST:**

- [ ] Use Python 3.12+
- [ ] Use `uv` for package management
- [ ] Configure Ruff for linting and formatting
- [ ] Configure mypy for type checking
- [ ] Include type hints for all public functions
- [ ] Follow Google docstring style
- [ ] Use structured logging (JSON in production)
- [ ] Implement custom exceptions
- [ ] Follow project structure conventions
- [ ] Use async/await for I/O operations
- [ ] Never store secrets in code
- [ ] Validate all input data

---

**Document maintained by:** Engineering Team
**Questions/Issues:** Open issue in respective repository or documentation repo
