FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create chromadb directory for persistence
RUN mkdir -p chromadb

# Expose gRPC port
EXPOSE 50051

# Run the search service
CMD ["python", "services/search/main.py"]

