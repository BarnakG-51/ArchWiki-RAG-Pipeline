FROM python:3.11-slim

WORKDIR /app

ENV PIP_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV PIP_EXTRA_INDEX_URL=https://pypi.org/simple

# Install PyTorch CPU version first (before other dependencies)
RUN pip install --no-cache-dir --index-url "https://download.pytorch.org/whl/cpu" "torch>=2.5,<2.6"

# Copy project files
COPY pyproject.toml ./
COPY shared ./shared
COPY services/brain ./services/brain

# Install dependencies
RUN pip install --no-cache-dir -e .

# Set working directory to brain service
WORKDIR /app/services/brain

# Expose port for gRPC server
EXPOSE 50052

# Run the brain service
CMD ["python", "main.py"]
