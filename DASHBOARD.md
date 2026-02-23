# Akash Autopilot - Futuristic Next.js Dashboard

A stunningly beautiful, real-time dashboard showcasing autonomous AI infrastructure operations on Akash Network.

## ✨ Features

- **🎨 Futuristic UI**: Animated gradients, glowing borders, and smooth transitions with Framer Motion
- **📊 Real-Time Stats**: Live action ledger, success rates, and AI decision metrics
- **🤖 AI Showcase**: Watch Llama 3.3 70B make autonomous decisions every 120 seconds
- **🎭 Demo Mode**: Pre-configured with 3 simulated deployments showing realistic infrastructure scenarios
- **⚡ Fast**: Next.js 15+ with Turbopack for instant HMR
- **📱 Responsive**: Works beautifully on desktop, tablet, and mobile

## 🚀 Quick Start (Development)

### Prerequisites
- Node.js 18+ and npm
- Running Akash Autopilot backend on `http://localhost:8000`

### Local Development

```bash
# Navigate to dashboard
cd dashboard

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🎯 Demo Mode Preview

The dashboard automatically connects to the FastAPI backend which, when `DEMO_MODE=true`:

```bash
# Terminal 1: Run Python backend
export DEMO_MODE=true
python -m src.api.server

# Terminal 2: Run dashboard
cd dashboard && npm run dev
```

## 📦 Production Deployment

### Build the Dashboard

```bash
cd dashboard
npm run build
npm start
```

### Docker Multi-Stage Build

```bash
# Build complete stack
docker build -f Dockerfile -t akash-autopilot:latest .

# Run with demo mode
docker run -p 8000:8000 -p 3000:3000 \
  -e DEMO_MODE=true \
  -e LOOP_INTERVAL=30 \
  akash-autopilot:latest
```

### Deploy to Akash

Update `deploy.yaml` to expose both ports:

```yaml
expose:
  - port: 8000      # FastAPI backend
    as: 8000
    to: [global: true]
  - port: 3000      # Next.js dashboard
    as: 3000
    to: [global: true]
```

## 🎨 Dashboard Sections

### Overview Tab
- **Why It's Cool**: Highlights the autonomous AI decision-making
- **Live Statistics**: Total actions, success rate, failed actions, loop iterations
- **Recent AI Decisions**: Real-time stream of actions taken by Llama 3.3 70B

### Action Ledger Tab
- Complete audit trail of all autonomous actions
- Timestamp, action type, deployment target, reason, and status
- Sortable, filterable, with terminal-style appearance

## 🔧 Architecture

```
┌─────────────────────────────────────────┐
│   Next.js Dashboard (Port 3000)         │
│   - Framer Motion animations            │
│   - Real-time data polling              │
│   - Beautiful Tailwind CSS styling      │
└─────────────────┬───────────────────────┘
                  │
                  │ API calls
                  ▼
┌─────────────────────────────────────────┐
│   FastAPI Backend (Port 8000)           │
│   - /status - Agent health              │
│   - /actions - Action ledger            │
│   - /policy - Current policy settings   │
│   - /health - Service health check      │
└─────────────────────────────────────────┘
```

## 📊 Real-Time Data Flow

```
Agent Loop (Every 120s)
    ↓
Fetches deployments (demo mode: generates 3 simulated)
    ↓
Sends to Llama 3.3 70B via AkashML
    ↓
Receives decision (scale_up, scale_down, redeploy, monitor)
    ↓
Executes action (demo mode: simulates success)
    ↓
Logs to database
    ↓
Dashboard polls /actions endpoint
    ↓
Displays with animations and styling
```

## 🎭 Demo Scenarios

When `DEMO_MODE=true`, each loop generates 3 random demo deployments:

1. **High CPU Usage** (85% CPU)
   - Expected action: `scale_up`
   - Shows AI scaling replicas from 2 → 4

2. **Memory Pressure** (90%+ RAM)
   - Expected action: `scale_up`
   - Shows AI responding to resource constraints

3. **High Error Rate** (15%+ errors)
   - Expected action: `redeploy`
   - Shows AI triggering redeployment

4. **Underutilized** (12% CPU)
   - Expected action: `scale_down`
   - Shows AI cost optimization

5. **Healthy Deployment** (optimal metrics)
   - Expected action: `monitor`
   - Shows AI maintains healthy systems

## 🎨 Styling Highlights

- **Glass Morphism**: Semi-transparent cards with backdrop blur
- **Neon Gradients**: Purple-pink-blue gradient text
- **Animated Orbs**: Floating gradient circles in background
- **Glowing Borders**: Colored text shadows and border glows
- **Smooth Transitions**: Framer Motion for all interactions
- **Terminal Aesthetic**: Monospace font for action ledger

## 🔌 Environment Variables

```bash
# Backend (FastAPI)
DEMO_MODE=true              # Enable simulated deployments
LOOP_INTERVAL=120           # Seconds between agent iterations
LOG_LEVEL=INFO              # Logging level

# Dashboard (handled automatically)
# Dashboard connects to NEXT_PUBLIC_API_URL 
# Defaults to current window origin
```

## 📖 Dependencies

### Backend
- FastAPI - REST API
- Uvicorn - ASGI server
- cosmpy - Cosmos SDK
- httpx - HTTP client for AkashML

### Dashboard
- Next.js 15+ - React framework
- Tailwind CSS - Utility CSS
- Framer Motion - Animation library
- Lucide React - Icon library

## 🐛 Troubleshooting

**Dashboard shows "Waiting for AI to analyze"**
- Make sure backend is running: `curl http://localhost:8000/health`
- Check CORS isn't blocking requests: `curl http://localhost:8000/actions`

**Actions not updating in real-time**
- Backend polling interval is 5 seconds (can be adjusted in page.tsx)
- Ensure demo mode is enabled for generated actions

**Build fails**
- Clear `.next` directory: `rm -rf dashboard/.next`
- Clear node_modules: `rm -rf dashboard/node_modules && npm ci`

## 📝 License

MIT - See LICENSE file

---

**Built with ❤️ for Akash Autopilot**

Autonomous Treasury + Infrastructure Operator running 100% on Akash Network
