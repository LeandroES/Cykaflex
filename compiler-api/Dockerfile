# ── Stage 1: dependency builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# gcc is needed to compile PLY C extensions
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy installed packages from builder — keeps image lean
COPY --from=builder /install /usr/local

# ghostscript: PS→PDF conversion  |  libgs-dev not needed at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for least-privilege execution
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --no-create-home appuser

# Application source (overridden by a bind-mount in dev)
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

# --reload enables hot-reloading when source is mounted as a volume
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
