# Quick Start Guide

Get Akash Autopilot running in 5 minutes.

## 🚀 Fastest Path (Local Testing)

```bash
# 1. Build and run with Docker Compose
docker-compose up -d

# 2. Check it's running
curl http://localhost:8000/health

# 3. View agent status
curl http://localhost:8000/status | jq

# 4. View logs
docker-compose logs -f
```

**Note**: This runs in MOCK mode (no real API calls) by default if you haven't set API keys.

---

## 🎯 Full Setup (With Real APIs)

### 1. Get API Keys

**Akash Console API**:
- Visit [console.akash.network](https://console.akash.network)
- Sign up / Login
- Navigate to API Keys section
- Create new API key

**AkashML API**:
- Visit [playground.akashml.com](https://playground.akashml.com)
- Sign up / Login
- Navigate to API Keys
- Create new API key

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env
```

Update these lines:
```bash
CONSOLE_API_KEY=your_actual_console_api_key
AKASHML_API_KEY=your_actual_akashml_api_key
```

### 3. Build & Run

```bash
# Build image
docker build -t akash-autopilot .

# Run with your keys
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  --env-file .env \
  akash-autopilot
```

### 4. Test Endpoints

```bash
# Health
curl http://localhost:8000/health

# Status (should show real loop running)
curl http://localhost:8000/status | jq

# Actions
curl http://localhost:8000/actions | jq

# Policy
curl http://localhost:8000/policy | jq
```

---

## 🌐 Deploy to Akash

### 1. Push to Docker Hub

```bash
# Login
docker login

# Tag with your username
docker tag akash-autopilot YOUR_USERNAME/akash-autopilot:latest

# Push
docker push YOUR_USERNAME/akash-autopilot:latest
```

### 2. Update deploy.yaml

Edit `deploy.yaml`:
```yaml
services:
  autopilot:
    image: YOUR_USERNAME/akash-autopilot:latest  # <- Change this
    env:
      - CONSOLE_API_KEY=your_api_key_here        # <- Change this
      - AKASHML_API_KEY=your_api_key_here        # <- Change this
```

### 3. Deploy

1. Go to [console.akash.network](https://console.akash.network)
2. Click "Deploy"
3. Choose "Upload SDL"
4. Upload `deploy.yaml`
5. Review and accept bid
6. Wait for deployment to start

### 4. Access Your Agent

After deployment:
```bash
# Get your deployment URL from Akash Console
# Then test:

curl https://YOUR_DEPLOYMENT_URL/health
curl https://YOUR_DEPLOYMENT_URL/status | jq
curl https://YOUR_DEPLOYMENT_URL/actions | jq
```

---

## 🔧 Using Makefile (Recommended)

```bash
# Build
make build

# Run locally
make run

# Check status
make status

# Check health
make health

# View actions
make actions

# View logs
make logs

# Stop
make stop

# Clean everything
make clean

# Push to Docker Hub
make push
```

---

## 🐛 Troubleshooting

### "Mock mode" message in logs

**Cause**: API keys not set or are placeholder values

**Fix**:
```bash
# Check your .env file
cat .env

# Make sure keys don't start with "your_"
CONSOLE_API_KEY=actual-key-here  # ✅
AKASHML_API_KEY=actual-key-here  # ✅
```

### Database permission errors

**Fix**:
```bash
# Make sure data directory is writable
mkdir -p data
chmod 777 data
```

### Can't connect to endpoints

**Fix**:
```bash
# Check container is running
docker ps

# Check logs
docker logs <container-id>

# Try health endpoint with verbose
curl -v http://localhost:8000/health
```

### Agent not making decisions

**Check**:
1. Is it running? `make status` → `"running": true`
2. Check loop count is increasing
3. View logs: `make logs`
4. In mock mode, it will always return "no_action"

---

## 📚 Next Steps

1. Read [README.md](README.md) for full documentation
2. Read [DEMO.md](DEMO.md) for presentation guide
3. Check out the code in `src/`
4. Customize policy settings in `.env`

---

## 💡 Quick Tips

**Fast iteration**:
```bash
# Rebuild and restart in one command
make clean && make build && make run && make logs
```

**Check everything is working**:
```bash
make test
```

**Monitor in real-time**:
```bash
# Terminal 1: Logs
make logs

# Terminal 2: Status checks
watch -n 5 'curl -s http://localhost:8000/status | jq .loop_count'
```

---

**Ready to deploy? See [README.md](README.md) for full guide!**
