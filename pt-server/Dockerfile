FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set workdir early
WORKDIR /app

# Copy only dependency files first to leverage Docker layer cache
COPY pyproject.toml uv.lock /app/

# Install dependencies (cached if dependency files unchanged)
RUN uv sync --frozen --no-cache

# Now copy the rest of the application
COPY . /app

# Run the application
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
