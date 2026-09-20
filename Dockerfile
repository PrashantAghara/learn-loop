FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run with uvicorn - logs go to stdout/stderr which Render captures
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]