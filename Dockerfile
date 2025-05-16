FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories with proper permissions
RUN mkdir -p /app/data && \
    chown -R nobody:nogroup /app/data && \
    chmod 777 /app/data

# Copy project files
COPY pyproject.toml ./
COPY app ./app
COPY .env ./

# Create and activate virtual environment, then install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install uv and project dependencies
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:////app/data/app.db

# Switch to non-root user
USER nobody

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]