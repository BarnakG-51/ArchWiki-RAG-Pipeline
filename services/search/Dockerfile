FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU version first (before other dependencies)
RUN pip install --no-cache-dir --index-url "https://download.pytorch.org/whl/cpu" "torch>=2.5,<2.6"

# Copy project files
COPY pyproject.toml ./
COPY shared ./shared
COPY services/search ./services/search

# Install dependencies
RUN pip install --no-cache-dir -e .

# Set working directory to search service
WORKDIR /app/services/search

# Expose port for gRPC server
EXPOSE 50051

# Run the search service
CMD ["python", "main.py"]
