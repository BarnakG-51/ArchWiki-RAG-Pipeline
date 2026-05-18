FROM python:3.11-slim

WORKDIR /app


ENV PIP_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV PIP_EXTRA_INDEX_URL=https://pypi.org/simple

# Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU version first (before other dependencies)
RUN pip install --no-cache-dir --index-url "https://download.pytorch.org/whl/cpu" "torch>=2.5,<2.6"

# Copy project files
COPY pyproject.toml ./
COPY shared ./shared
COPY services/ingestion ./services/ingestion

# Install dependencies
RUN pip install --no-cache-dir -e .

# Set working directory to ingestion service
WORKDIR /app/services/ingestion

# Run the ingestion service
CMD ["python", "main.py"]
