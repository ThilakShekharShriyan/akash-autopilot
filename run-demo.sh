#!/bin/bash
# Run both backend and dashboard for local testing

echo "🚀 Starting Akash Autopilot with futuristic Next.js dashboard..."
echo ""

# Kill any existing processes on ports 8000 and 3000
lsof -ti :8000 | xargs kill -9 2>/dev/null
lsof -ti :3000 | xargs kill -9 2>/dev/null

echo "📦 Building and starting FastAPI backend..."
docker remove akash-autopilot-demo 2>/dev/null || true
docker run -d \
  --name akash-autopilot-demo \
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

echo "⏳ Waiting for backend to be ready..."
sleep 5

echo "🎨 Starting Next.js dashboard..."
cd dashboard && npm run dev &
DASHBOARD_PID=$!

echo ""
echo "✅ All systems ready!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Open your browser:"
echo "   Dashboard: http://localhost:3000"
echo "   API: http://localhost:8000/health"
echo ""
echo "📊 Watch AI make autonomous decisions in real-time!"
echo "   - Analyzes metrics every 30 seconds (demo)"
echo "   - Scales deployments based on resource usage"
echo "   - All actions logged with beautiful animations"
echo ""
echo "🛑 To stop everything:"
echo "   1. Press Ctrl+C in this terminal"
echo "   2. docker stop akash-autopilot-demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running
wait $DASHBOARD_PID
