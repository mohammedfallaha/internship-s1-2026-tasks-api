# Tasks API

A small Tasks API built with FastAPI and Python 3.12.

## Requirements

- Python 3.12
- uv

## Run the API

uv sync
uv run fastapi dev main.py

# The API will be available at:

http://127.0.0.1:8000

# Interactive API documentation:

http://127.0.0.1:8000/docs

# Run tests
uv run pytest

# Code quality and Format the code:

uv run ruff format .


# Check the code:

uv run ruff check .

# Run the database This starts the database container and creates or updates the database schema to match the latest migration.

Start PostgreSQL using Docker Compose:

docker compose up -d

Apply database migrations:

uv run alembic upgrade head

