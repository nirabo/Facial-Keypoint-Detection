# syntax=docker/dockerfile:1.9

# =============================================================================
# Facial Keypoint Detection - Multi-stage Dockerfile
# =============================================================================

# --- Stage 1: Base ---
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for OpenCV and ML
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

WORKDIR /app

# --- Stage 2: Dependencies ---
FROM base AS dependencies

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install production dependencies only
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project || \
    uv sync --no-dev --no-install-project

# --- Stage 3: Development (with Jupyter) ---
FROM dependencies AS development

# Install all dependencies including dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project || \
    uv sync --no-install-project

# Copy application code
COPY --chown=mluser:mluser src/ /app/src/
COPY --chown=mluser:mluser notebooks/ /app/notebooks/
COPY --chown=mluser:mluser detector_architectures/ /app/detector_architectures/
COPY --chown=mluser:mluser images/ /app/images/

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

USER mluser

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]

# --- Stage 4: Training (CPU) ---
FROM base AS training

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY --chown=mluser:mluser src/ /app/src/
COPY --chown=mluser:mluser detector_architectures/ /app/detector_architectures/

ENV PATH="/app/.venv/bin:$PATH"

USER mluser

# Default: run training module
CMD ["python", "-m", "facial_keypoints.train"]

# --- Stage 5: Training (GPU with NVIDIA CUDA) ---
FROM nvidia/cuda:12.2.0-cudnn8-runtime-ubuntu22.04 AS training-gpu

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files and install
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project || \
    uv sync --no-dev --no-install-project

# Copy application code
COPY --chown=mluser:mluser src/ /app/src/
COPY --chown=mluser:mluser detector_architectures/ /app/detector_architectures/

ENV PATH="/app/.venv/bin:$PATH"

USER mluser

CMD ["python", "-m", "facial_keypoints.train"]

# --- Stage 6: Inference ---
FROM base AS inference

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY --chown=mluser:mluser src/ /app/src/
COPY --chown=mluser:mluser detector_architectures/ /app/detector_architectures/

ENV PATH="/app/.venv/bin:$PATH"

USER mluser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import facial_keypoints; print('ok')" || exit 1

CMD ["python", "-m", "facial_keypoints.inference"]
