.PHONY: help build run stop clean test push deploy

# Default target
help:
	@echo "Akash Autopilot - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make build       - Build Docker image"
	@echo "  make run         - Run with docker-compose"
	@echo "  make stop        - Stop containers"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Open shell in container"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run tests (if any)"
	@echo "  make health      - Check health endpoint"
	@echo "  make status      - Check agent status"
	@echo ""
	@echo "Deployment:"
	@echo "  make push        - Push image to Docker Hub"
	@echo "  make deploy      - Deploy to Akash (manual)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make clean-all   - Remove everything including images"

# Build Docker image
build:
	@echo "Building Docker image..."
	docker build -t akash-autopilot:latest .

# Run with docker-compose
run:
	@echo "Starting Akash Autopilot..."
	docker-compose up -d
	@echo ""
	@echo "Agent running at http://localhost:8000"
	@echo "Check status: make status"
	@echo "View logs: make logs"

# Stop containers
stop:
	@echo "Stopping containers..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f autopilot

# Open shell in container
shell:
	docker-compose exec autopilot /bin/bash

# Check health
health:
	@echo "Checking health endpoint..."
	@curl -s http://localhost:8000/health | jq

# Check agent status
status:
	@echo "Checking agent status..."
	@curl -s http://localhost:8000/status | jq

# View recent actions
actions:
	@echo "Fetching recent actions..."
	@curl -s http://localhost:8000/actions | jq

# View policy
policy:
	@echo "Fetching policy settings..."
	@curl -s http://localhost:8000/policy | jq

# View deployments
deployments:
	@echo "Fetching tracked deployments..."
	@curl -s http://localhost:8000/deployments | jq

# Push to Docker Hub
push:
	@echo "Enter your Docker Hub username:"
	@read username; \
	docker tag akash-autopilot:latest $$username/akash-autopilot:latest; \
	docker push $$username/akash-autopilot:latest
	@echo "Image pushed successfully!"

# Clean containers and volumes
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	rm -rf data/

# Clean everything including images
clean-all: clean
	@echo "Removing Docker images..."
	docker rmi akash-autopilot:latest || true

# Quick test
test: build run
	@echo "Waiting for container to start..."
	@sleep 5
	@echo "\nRunning health check..."
	@make health
	@echo "\nRunning status check..."
	@make status
	@echo "\nTests complete!"

# Install dependencies locally (for development)
install:
	pip install -r requirements.txt

# Format code
format:
	black src/
	isort src/

# Lint code
lint:
	pylint src/
	flake8 src/
