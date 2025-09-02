# syntax=docker/dockerfile:1

# Multi-stage build for efficiency and smaller runtime image
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# Install system dependencies (build/libpq for psycopg2, curl for health/debug)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to keep image clean
RUN python -m venv /venv

WORKDIR /app

# Install Python requirements first to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy project
COPY . /app

# Create non-root user for security
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# Expose the expected port (3000 as per instructions)
EXPOSE 3000

# Entrypoint handles migrations, collectstatic, and superuser creation
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command runs Gunicorn bound to port 3000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:3000", "--workers", "3", "--timeout", "120"]
