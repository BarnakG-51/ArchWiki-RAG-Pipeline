FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -e .

# Run the brain service
CMD ["python", "services/brain/main.py"]

