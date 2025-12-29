FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies for graphviz and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY app /app/app
COPY resilience /app/resilience
COPY routing /app/routing
COPY cost_control /app/cost_control
COPY caching /app/caching
COPY security /app/security
COPY quality /app/quality
COPY features /app/features

# Create volumes for policy hot reload (optional, can be mounted)
VOLUME ["/app/resilience/policies", "/app/routing/policies", "/app/cost_control/policies", \
        "/app/caching/policies", "/app/security/policies", "/app/quality/policies", "/app/features/policies"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

