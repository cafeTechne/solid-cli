FROM python:3.11-slim

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install solid-cli and dependencies
RUN pip install --no-cache-dir .

# Copy source code
COPY solid_cli ./solid_cli

# Set entrypoint
ENTRYPOINT ["solid"]
