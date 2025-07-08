FROM python:3.12-slim AS base

ENV \
    PYTHONPATH=/app:/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.1.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y curl openssl && rm -rf /var/lib/apt/lists/*
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Development stage
FROM base AS development
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR
COPY . .
CMD ["python", "main.py"]

# Production stage  
FROM base AS production
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only=main && \
    pip install gunicorn && \
    poetry cache clear --all pypi
    
COPY . .

EXPOSE 8000 8443

ENTRYPOINT ["sh", "-c", "chmod +x ./generate-cert.sh && ./generate-cert.sh && gunicorn --worker-class uvicorn.workers.UvicornWorker --workers ${WORKERS:-2} --bind 0.0.0.0:8443 --certfile=/app/certs/cert.pem --keyfile=/app/certs/key.pem main:app"]