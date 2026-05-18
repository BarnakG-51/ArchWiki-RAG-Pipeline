# Running the ArchWiki RAG Pipeline with Docker

## Prerequisites

Before running the pipeline, ensure you have:

- **Docker** (v20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v2.0+) - Usually included with Docker Desktop
- **NVIDIA GPU** (recommended) - For LLM inference with vLLM
- **NVIDIA Container Runtime** - [Install nvidia-docker](https://github.com/NVIDIA/nvidia-docker)
- **4GB+ RAM** (8GB+ recommended)
- **10GB+ disk space** for models

### System Check

```bash
# Verify Docker installation
docker --version
docker-compose --version

# Check GPU availability
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

## Quick Start (5 minutes)

### 1. Navigate to Project Directory
```bash
cd /run/media/barnak/01DC4B19B0F98380/projects/mega_pipeline
```

### 2. Build Docker Images
```bash
# Build all services
docker-compose build

# Or with progress output
docker-compose build --progress=plain
```

### 3. Start the Pipeline
```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Services are Running
```bash
# Check container status
docker-compose ps

# Expected output:
# brain       - running on port 50052
# search      - running on port 50051
# ingestion   - running (data processing)
# llm-engine  - running on port 8000
```

## Running Individual Services

### LLM Engine Only
```bash
docker-compose up llm-engine
# Accessible at: http://localhost:8000
```

### Start Services in Specific Order
```bash
# Terminal 1: LLM Engine
docker-compose up llm-engine

# Terminal 2: Search Service (depends on chromadb)
docker-compose up search

# Terminal 3: Brain Service
docker-compose up brain

# Terminal 4: Ingestion Pipeline
docker-compose up ingestion
```

## Interacting with the Pipeline

### 1. Test LLM Engine
```bash
curl http://localhost:8000/v1/models
# Should return available models
```

### 2. Query the Brain Service (gRPC)
The brain service listens on port 50052. Use a gRPC client:

```bash
# Using grpcurl (install: https://github.com/fullstorydev/grpcurl)
grpcurl -plaintext localhost:50052 list
```

### 3. Check Search Service
```bash
docker-compose exec search curl localhost:50051
```

### 4. Access Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f brain

# Last 50 lines
docker-compose logs --tail=50 brain
```

## Data Management

### Persistent Data
Data is stored in `./data` volume:
```bash
# View stored data
ls -la ./data

# Persist data across restarts
# Volumes are defined in docker-compose.yml
```

### Clear All Data
```bash
# Stop containers
docker-compose down

# Remove volumes
docker volume prune

# Clean up
docker-compose down -v  # Removes named volumes
```

## Environment Variables

Configure via environment in docker-compose.yml:

```yaml
environment:
  - LLM_API_URL=http://llm-engine:8000/v1
  - SEARCH_SERVICE_HOST=search
  - SEARCH_SERVICE_PORT=50051
  - LOG_LEVEL=INFO
```

## Troubleshooting

### Container Won't Start
```bash
# View error logs
docker-compose logs brain

# Rebuild from scratch
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

### Out of Memory
```bash
# Check resource usage
docker stats

# Reduce model size (edit docker-compose.yml)
# Change --model to a smaller variant
```

### GPU Not Detected
```bash
# Verify GPU setup
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all ubuntu nvidia-smi

# If failing, install nvidia-docker:
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### ChromaDB Connection Issues
```bash
# Restart services to reinitialize DB
docker-compose restart search

# Check chromadb volume
docker volume ls | grep chromadb
```

## Production Deployment

### Scale Services
```bash
# Run multiple replicas
docker-compose up -d --scale brain=3
```

### Using .env File
Create `.env`:
```env
LLM_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
LLM_MAX_TOKENS=4096
SEARCH_TOP_K=3
```

Reference in docker-compose.yml:
```yaml
environment:
  - LLM_MODEL=${LLM_MODEL}
```

### Health Checks
Add to docker-compose.yml:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:50051/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Performance Tips

1. **GPU Allocation**: Ensure GPU memory is available
2. **Model Caching**: First run downloads model (~4GB)
3. **Network**: Use `rag-network` bridge network (auto-configured)
4. **Storage**: Use named volumes for persistence

## Stop and Clean Up

```bash
# Stop all running containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove unused images
docker image prune
```

## Useful Commands

```bash
# Execute command in running container
docker-compose exec brain python -c "import services.brain.main"

# View service logs
docker-compose logs --follow brain

# Rebuild specific service
docker-compose build brain

# Remove all containers and networks
docker-compose down --remove-orphans

# Show resource usage
docker stats
```

## Next Steps

1. **Configure ingestion**: Add Arch Wiki pages to scrape
2. **Test queries**: Send questions to the brain service
3. **Monitor performance**: Watch GPU/memory usage with `docker stats`
4. **Deploy**: Push to registry and deploy to production

---

For more help, see:
- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
