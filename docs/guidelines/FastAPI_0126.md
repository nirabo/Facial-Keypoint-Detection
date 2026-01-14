# FastAPI Best Practices Guide

**Document Version:** 2.0
**Created:** February 14, 2024
**Last Updated:** January 6, 2026
**Status:** Active Standard

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Application Setup](#application-setup)
- [Code Organization](#code-organization)
- [API Design](#api-design)
- [Pydantic v2 Models](#pydantic-v2-models)
- [Database Integration](#database-integration)
- [Security Best Practices](#security-best-practices)
- [Performance Optimization](#performance-optimization)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Documentation](#documentation)
- [Dependency Management](#dependency-management)

---

## Overview

This document establishes FastAPI development standards for all backend services. These practices ensure consistent, secure, and performant APIs.

**Key Technologies (2025/2026):**

- **FastAPI** 0.115+ with async support
- **Pydantic v2** (2.10+) for data validation
- **SQLAlchemy 2.0+** with async support
- **Python 3.12+** (3.13 recommended)
- **uv** for package management
- **Ruff** for linting/formatting

---

## Project Structure

### Recommended Project Layout

```
my_fastapi_project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # Application entry point
│       ├── config.py               # Configuration management
│       ├── database.py             # Database setup
│       ├── dependencies.py         # Shared dependencies
│       │
│       ├── api/                    # API layer
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── router.py       # API router aggregation
│       │   │   ├── users.py        # User endpoints
│       │   │   ├── auth.py         # Auth endpoints
│       │   │   └── items.py        # Item endpoints
│       │   └── deps.py             # API dependencies
│       │
│       ├── core/                   # Core functionality
│       │   ├── __init__.py
│       │   ├── security.py         # Auth utilities
│       │   └── middleware.py       # Custom middleware
│       │
│       ├── models/                 # SQLAlchemy models
│       │   ├── __init__.py
│       │   ├── base.py             # Base model class
│       │   ├── user.py
│       │   └── item.py
│       │
│       ├── schemas/                # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── base.py             # Base schema class
│       │   ├── user.py
│       │   └── item.py
│       │
│       ├── services/               # Business logic
│       │   ├── __init__.py
│       │   ├── user_service.py
│       │   └── auth_service.py
│       │
│       ├── repositories/           # Data access layer
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── user_repository.py
│       │
│       └── exceptions/             # Custom exceptions
│           ├── __init__.py
│           └── handlers.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/                        # Database migrations
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

### Module Organization

- Use domain-driven design principles
- Separate business logic from API endpoints
- Implement repository pattern for data access
- Use dependency injection for better testability
- Keep routers thin, move logic to services

---

## Application Setup

### Main Application with Lifespan

**app/main.py:**

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.database import engine
from app.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    # Initialize database connection pool, cache, etc.
    await engine.connect()

    yield

    # Shutdown
    # Close connections, cleanup resources
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="API Description",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs" if settings.SHOW_DOCS else None,
        redoc_url="/redoc" if settings.SHOW_DOCS else None,
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
```

### Configuration with Pydantic Settings

**app/config.py:**

```python
from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "My API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SHOW_DOCS: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: RedisDsn | None = None

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

---

## Code Organization

### Best Practices

1. Use Pydantic v2 models for request/response validation
2. Implement dependency injection using FastAPI's dependency system
3. Use async/await for I/O-bound operations
4. Implement proper error handling with HTTPException
5. Use status codes consistently
6. Keep routes organized by domain/resource

### Router Organization

**app/api/v1/router.py:**

```python
from fastapi import APIRouter

from app.api.v1 import auth, items, users


api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["Items"],
)
```

**app/api/v1/users.py:**

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    skip: int = 0,
    limit: int = 100,
) -> list[UserResponse]:
    """List all users with pagination."""
    return await service.get_users(skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Get user by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Create a new user."""
    user = await service.create_user(user_in)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update user by ID."""
    user = await service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Delete user by ID."""
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
```

---

## API Design

### RESTful Principles

1. Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
2. Implement proper status codes
3. Use consistent URL naming conventions (plural nouns)
4. Version your APIs (`/api/v1/...`)
5. Implement proper pagination
6. Use query parameters for filtering/sorting

### Response Format

**Standard Success Response:**

```python
from pydantic import BaseModel
from typing import Generic, TypeVar


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class SingleResponse(BaseModel, Generic[T]):
    """Single item response wrapper."""

    data: T


# Usage in endpoint
@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = 1,
    per_page: int = 20,
) -> PaginatedResponse[UserResponse]:
    """List users with pagination."""
    ...
```

**Standard Error Response:**

```python
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail model."""

    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    details: list[ErrorDetail] | None = None
```

### Pagination

```python
from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Query(1, ge=1, description="Page number")
    per_page: int = Query(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.per_page


# Usage
@router.get("")
async def list_items(
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[ItemResponse]:
    """List items with pagination."""
    ...
```

---

## Pydantic v2 Models

### Base Schema

**app/schemas/base.py:**

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode (was orm_mode in v1)
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime
    updated_at: datetime | None = None
```

### User Schemas

**app/schemas/user.py:**

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user (all fields optional)."""

    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserWithToken(BaseModel):
    """User response with authentication token."""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
```

### Pydantic v2 Key Differences

```python
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class ExampleSchema(BaseModel):
    """Example showing Pydantic v2 features."""

    name: str
    value: int

    # v2: ConfigDict instead of inner Config class
    model_config = ConfigDict(
        from_attributes=True,  # was orm_mode
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    # v2: field_validator with mode parameter
    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: str) -> str:
        """Clean name before validation."""
        return v.strip().lower()

    # v2: model_validator for multi-field validation
    @model_validator(mode="after")
    def validate_model(self) -> "ExampleSchema":
        """Validate entire model."""
        if self.value < 0 and self.name == "positive":
            raise ValueError("Value must be positive when name is 'positive'")
        return self
```

---

## Database Integration

### Async SQLAlchemy Setup

**app/database.py:**

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### SQLAlchemy 2.0 Models

**app/models/base.py:**

```python
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Mixin for timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )
```

**app/models/user.py:**

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    items: Mapped[list["Item"]] = relationship(back_populates="owner")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
```

### Repository Pattern

**app/repositories/base.py:**

```python
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, id: int) -> ModelType | None:
        """Get by ID."""
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get all with pagination."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create new record."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update record."""
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete record."""
        await self.session.delete(obj)
        await self.session.flush()
```

---

## Security Best Practices

### JWT Authentication

**app/core/security.py:**

```python
from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        **(extra_claims or {}),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
```

### Authentication Dependencies

**app/api/deps.py:**

```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get(int(user_id))

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware


# In production, specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ["https://myapp.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest) -> TokenResponse:
    """Login with rate limiting."""
    ...
```

---

## Performance Optimization

### Database Optimization

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload


# Eager loading to prevent N+1 queries
async def get_user_with_items(user_id: int) -> User | None:
    """Get user with eagerly loaded items."""
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.items))
    )
    return result.scalar_one_or_none()


# Efficient pagination
from sqlalchemy import func


async def get_users_paginated(page: int, per_page: int) -> tuple[list[User], int]:
    """Get users with total count in single transaction."""
    # Count query
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar_one()

    # Data query
    result = await db.execute(
        select(User)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    users = list(result.scalars().all())

    return users, total
```

### Background Tasks

```python
from fastapi import BackgroundTasks


@router.post("/users")
async def create_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> UserResponse:
    """Create user and send welcome email in background."""
    user = await user_service.create_user(user_in)

    # Don't block response for email
    background_tasks.add_task(
        send_welcome_email,
        email=user.email,
        name=user.name,
    )

    return UserResponse.model_validate(user)
```

### Caching with Redis

```python
from functools import wraps
from typing import Callable

import redis.asyncio as redis


redis_client = redis.from_url(settings.REDIS_URL)


def cache(expire: int = 60):
    """Cache decorator for async functions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache first
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await redis_client.setex(cache_key, expire, json.dumps(result))

            return result
        return wrapper
    return decorator


# Usage
@cache(expire=300)
async def get_user_stats(user_id: int) -> dict:
    """Get user statistics (cached for 5 minutes)."""
    ...
```

---

## Error Handling

### Exception Handlers

**app/exceptions/handlers.py:**

```python
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions import (
    AppException,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "not_found",
                "message": str(exc),
            },
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        request: Request,
        exc: UnauthorizedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "unauthorized",
                "message": str(exc),
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(
        request: Request,
        exc: ForbiddenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "forbidden",
                "message": str(exc),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": [
                    {
                        "field": ".".join(str(loc) for loc in err["loc"]),
                        "message": err["msg"],
                    }
                    for err in exc.errors()
                ],
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred",
            },
        )
```

---

## Testing

### Test Configuration

**tests/conftest.py:**

```python
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app


# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    settings.DATABASE_URL.path,
    f"{settings.DATABASE_URL.path}_test",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(str(TEST_DATABASE_URL))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for each test."""
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
```

### Test Examples

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    """Test user creation endpoint."""
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient) -> None:
    """Test 404 for non-existent user."""
    response = await client.get("/api/v1/users/99999")

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
```

---

## Documentation

### OpenAPI Documentation

```python
from fastapi import FastAPI


app = FastAPI(
    title="My API",
    description="""
## Overview

This API provides...

## Authentication

Use Bearer token authentication:
```

Authorization: Bearer <token>

```

## Rate Limiting

- Login: 5 requests per minute
- API: 100 requests per minute
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
```

### Endpoint Documentation

```python
from fastapi import APIRouter, Path, Query


router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a single user by their unique identifier.",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: int = Path(..., description="The unique identifier of the user", ge=1),
) -> UserResponse:
    """
    Get a user by their ID.

    - **user_id**: The unique identifier of the user (must be positive)
    """
    ...
```

---

## Dependency Management

### pyproject.toml

```toml
[project]
name = "my-api"
version = "1.0.0"
description = "My FastAPI application"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[argon2]>=1.7.4",
    "httpx>=0.28.0",
    "redis>=5.2.0",
    "structlog>=24.4.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

---

## Summary Checklist

**Every FastAPI service MUST:**

- [ ] Use FastAPI 0.115+ with Pydantic v2
- [ ] Use async database drivers (asyncpg, databases)
- [ ] Implement lifespan context manager for startup/shutdown
- [ ] Use dependency injection for database sessions
- [ ] Implement proper error handling with custom exceptions
- [ ] Use Pydantic v2 schemas for all request/response models
- [ ] Implement authentication with JWT
- [ ] Add CORS middleware with specific origins
- [ ] Include health check endpoint
- [ ] Configure OpenAPI documentation
- [ ] Achieve 80%+ test coverage
- [ ] Use structured logging

---

**Document maintained by:** Engineering Team
**Last Updated:** January 6, 2026
