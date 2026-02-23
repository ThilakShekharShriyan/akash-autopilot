#!/bin/bash
# Quick local test script for Akash Autopilot

echo "🧪 Testing Akash Autopilot locally with demo mode..."
echo ""

# Stop and remove any existing container
docker stop akash-autopilot-test 2>/dev/null || true
docker rm akash-autopilot-test 2>/dev/null || true

# Build the image locally
echo "📦 Building Docker image..."
docker build -t akash-autopilot-test .

# Run locally with demo mode
echo "🚀 Starting container with demo mode..."
docker run -d \
  --name akash-autopilot-test \
  -p 8000:8000 \
  -e DEMO_MODE=true \
  -e LOOP_INTERVAL=30 \
  -e LOG_LEVEL=INFO \
  -e CONSOLE_API_KEY=ac.sk.production.211dad6023cd3bb9ce752b4602893bfb01fda4d7d8335ed925ff924bbdd17c17 \
  -e CONSOLE_API_BASE_URL=https://console-api.akash.network \
  -e AKASHML_API_KEY=akml-yluUEjWbDvSVerKCXZkBYhzUPlKfzDZN \
  -e AKASHML_BASE_URL=https://api.akashml.com/v1 \
  -e AKASHML_MODEL=meta-llama/Llama-3.3-70B-Instruct \
  -e WALLET_MNEMONIC="" \
  akash-autopilot-test

echo ""
echo "✅ Container started! Watching logs..."
echo "   Dashboard: http://localhost:8000"
echo "   API: http://localhost:8000/status"
echo ""
echo "Press Ctrl+C to stop watching logs (container keeps running)"
echo "Run 'docker stop akash-autopilot-test' to stop the container"
echo ""

# Follow logs
docker logs -f akash-autopilot-test
