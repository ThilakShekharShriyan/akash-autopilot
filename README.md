# 🤖 Akash Autopilot

**Autonomous Infrastructure Operator for Akash Network**

An AI-powered agent that continuously monitors Akash deployments, uses AkashML for intelligent decision-making, and automatically executes infrastructure actions (scaling, redeploying) based on policy guardrails. Features persistent state, restart resilience, and a complete audit trail.

---

## 🌟 Features

- ✅ **Fully Autonomous**: Continuous loop operation with no manual intervention
- ✅ **AI-Powered Reasoning**: Uses AkashML (Llama 3.3 70B) for intelligent decisions
- ✅ **Infrastructure Actions**: Scale deployments and trigger redeploys via Console API
- ✅ **Policy Guardrails**: Rate limits, cooldowns, and safety constraints
- ✅ **Persistent State**: SQLite database survives container restarts
- ✅ **Audit Trail**: Complete action ledger with timestamps and status
- ✅ **REST API**: Monitor agent status, actions, and deployments
- ✅ **Runs on Akash**: Deployed entirely on Akash Network

---

## 📁 Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── loop.py            # Main autonomous loop
│   │   ├── llm.py             # AkashML integration
│   │   ├── console_api.py     # Akash Console API client
│   │   └── policy.py          # Policy guardrails
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py          # FastAPI endpoints
│   └── database/
│       ├── __init__.py
│       └── db.py              # SQLite persistence layer
├── Dockerfile
├── deploy.yaml                # Akash SDL
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Hub account
- Akash Console account with API key
- AkashML API key ([Sign up here](https://playground.akashml.com))
- Basic knowledge of Akash Network

### Step 1: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd Akash

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
```bash
CONSOLE_API_KEY=your_actual_console_api_key
AKASHML_API_KEY=your_actual_akashml_api_key
```

### Step 2: Build Docker Image

```bash
# Build image
docker build -t your-dockerhub-username/akash-autopilot:latest .

# Test locally (mock mode)
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e CONSOLE_API_KEY=your_test_key \
  -e AKASHML_API_KEY=your_test_key \
  your-dockerhub-username/akash-autopilot:latest

# Check health (in another terminal)
curl http://localhost:8000/health
```

### Step 3: Push to Docker Hub

```bash
docker login
docker push your-dockerhub-username/akash-autopilot:latest
```

### Step 4: Deploy on Akash

1. Update [deploy.yaml](deploy.yaml):
   - Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username
   - Update environment variables with your API keys

2. Deploy via [Akash Console](https://console.akash.network):
   - Click "Deploy"
   - Upload `deploy.yaml`
   - Accept bids
   - Get deployment URL

3. Verify deployment:
```bash
# Check health
curl https://<your-deployment-url>/health

# Check agent status
curl https://<your-deployment-url>/status

# View recent actions
curl https://<your-deployment-url>/actions
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONSOLE_API_KEY` | Akash Console API key | Required |
| `AKASHML_API_KEY` | AkashML API key | Required |
| `LOOP_INTERVAL` | Seconds between loop iterations | `120` |
| `MAX_ACTIONS_PER_HOUR` | Rate limit per hour | `10` |
| `MAX_ACTIONS_PER_DAY` | Rate limit per day | `50` |
| `SCALE_COOLDOWN_SECONDS` | Cooldown after scaling | `3600` |
| `REDEPLOY_COOLDOWN_SECONDS` | Cooldown after redeploy | `7200` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Policy Guardrails

The agent enforces the following safety rules:

- **Rate Limits**: Maximum actions per hour/day
- **Cooldowns**: Prevents repeated actions on same deployment
- **Replica Limits**: 0-10 replicas per deployment
- **Action Validation**: LLM responses validated before execution

---

## 📡 API Endpoints

### Health & Status

```bash
GET /health              # Health check for providers
GET /status              # Agent status and stats
GET /stats               # Database statistics
```

### Actions

```bash
GET /actions             # Recent actions (default: 50)
GET /actions/{type}      # Actions by type (scale, redeploy)
```

### Deployments

```bash
GET /deployments         # All tracked deployments
GET /deployments/{id}    # Specific deployment state
```

### Policy

```bash
GET /policy              # Current policy settings
```

---

## 🎯 How It Works

### Agent Loop (Every 120 seconds)

1. **Cleanup**: Remove expired cooldowns
2. **Fetch**: Get deployment states from Console API
3. **Analyze**: Send metrics to AkashML for reasoning
4. **Validate**: Check LLM response against policy
5. **Execute**: Perform approved actions
6. **Log**: Record action in audit ledger
7. **Cooldown**: Apply cooldown period
8. **Repeat**: Wait for next interval

### Decision Flow

```
Deployment Metrics
        ↓
    AkashML LLM
        ↓
   Action Plan (JSON)
        ↓
  Policy Validation
        ↓
    Action Execution
        ↓
   Database Logging
        ↓
  Cooldown Applied
```

---

## 🧪 Testing Locally

### Mock Mode (No API Keys Required)

```bash
# Run with mock APIs for testing
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e CONSOLE_API_KEY=your_test_key \
  -e AKASHML_API_KEY=your_test_key \
  your-dockerhub-username/akash-autopilot:latest

# Mock mode auto-detects placeholder keys
# Returns fake deployments and no-action decisions
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/status | jq

# View actions
curl http://localhost:8000/actions | jq

# View policy
curl http://localhost:8000/policy | jq
```

---

## 📊 Database Schema

### Tables

- **`action_ledger`**: Audit log of all actions
- **`deployment_state`**: Current deployment tracking
- **`cooldowns`**: Active cooldown periods
- **`policy`**: Policy configuration values

### Action Ledger Example

```json
{
  "id": 1,
  "timestamp": "2026-02-21T12:00:00",
  "action_type": "scale",
  "deployment_id": "12345",
  "details": "{\"new_count\": 2, \"reason\": \"High CPU usage\"}",
  "status": "completed",
  "error": null
}
```

---

## 🔒 Security Considerations

- **API Keys**: Passed as environment variables (not baked into image)
- **Non-root User**: Container runs as non-root user `autopilot`
- **Rate Limits**: Prevents runaway execution
- **Cooldowns**: Prevents rapid repeated actions
- **Action Validation**: All LLM decisions checked against policy

⚠️ **For Production**: Use secret management (Akash Provider secrets, Vault, etc.)

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs <container-id>

# Verify environment variables
docker inspect <container-id> | grep -A 20 Env
```

### Database Errors

```bash
# Check persistent volume mount
docker exec <container-id> ls -la /data

# Check database permissions
docker exec <container-id> ls -l /data/autopilot.db
```

### API Connection Issues

```bash
# Test Console API
curl -H "x-api-key: YOUR_KEY" \
  https://console-api.akash.network/v1/deployments

# Test AkashML API
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.akashml.com/v1/models
```

---

## 🚧 Known Limitations (MVP)

- ✅ **Implemented**: Loop, database, policy, API, AkashML integration
- ⚠️ **Partially Implemented**: Console API integration (structure ready)
- 🔨 **Future Work**:
  - SDL parsing and modification for actual scaling
  - Redeploy trigger via Console API
  - Real-time metrics collection
  - Multi-deployment orchestration

---

## 📈 Future Enhancements

- [ ] SDL template management and modification
- [ ] Real-time metrics from Akash providers
- [ ] Webhook notifications (Discord, Slack)
- [ ] Cost optimization recommendations
- [ ] Multi-region deployment strategies
- [ ] Integration with blockchain treasury operations
- [ ] Grafana dashboard for visualization

---

## 🤝 Contributing

This is a hackathon project! Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- **Akash Network** - Decentralized cloud platform
- **AkashML** - AI inference on Akash
- **Cosmos Ecosystem** - Blockchain infrastructure

---

## 📞 Support

- Akash Discord: [discord.gg/akash](https://discord.gg/akash)
- Akash Docs: [akash.network/docs](https://akash.network/docs)
- AkashML: [playground.akashml.com](https://playground.akashml.com)

---

**Built for the Akash Hackathon 2026** 🚀
