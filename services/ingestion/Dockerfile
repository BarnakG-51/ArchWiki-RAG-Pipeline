FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create data directories
RUN mkdir -p data/raw chromadb

# Run the ingestion service
CMD ["python", "services/ingestion/main.py"]

