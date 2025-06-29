# Multi-stage build for smaller image size
FROM python:3.12-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-cache

# Production stage
FROM python:3.12-slim

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Direct uvicorn command (faster than uv run)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
