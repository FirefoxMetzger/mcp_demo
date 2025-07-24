# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install uv (https://github.com/astral-sh/uv)
RUN pip install --no-cache-dir uv

# Expose the port uvicorn will run on
EXPOSE 8000

# Set workdir
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync

# Copy the rest of the code
COPY main.py .
COPY src/ ./src/

ARG domain
ENV domain=${domain}

CMD ["uv", "run", \
     "uvicorn", \
     "main:app", \
     "--ssl-keyfile", "/app/src/static/ssl_privatekey.pem", \
     "--ssl-certfile", "/app/src/static/ssl_fullchain.pem", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
