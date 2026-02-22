# 🎬 Demo Scenario Guide

This guide walks through a complete demo of Akash Autopilot for presentations.

---

## 🎯 Demo Objectives

1. **Show Autonomy**: Agent runs continuously without manual intervention
2. **Show AI Reasoning**: AkashML makes intelligent decisions
3. **Show Persistence**: Database survives container restarts
4. **Show Policy Enforcement**: Guardrails prevent unsafe actions
5. **Show Audit Trail**: Complete action history with timestamps

---

## 📋 Pre-Demo Checklist

- [ ] Docker image built and pushed to Docker Hub
- [ ] Akash Console API key obtained
- [ ] AkashML API key obtained
- [ ] deploy.yaml updated with your image and keys
- [ ] Deployment successfully running on Akash
- [ ] Browser tabs prepared (see below)

### Browser Tabs to Prepare

1. Akash Console (deployment view)
2. `https://<your-deployment-url>/status` (agent status)
3. `https://<your-deployment-url>/actions` (action log)
4. `https://<your-deployment-url>/deployments` (deployment tracking)
5. `https://<your-deployment-url>/policy` (policy view)

---

## 🎪 Demo Script (3 Minutes)

### **Part 1: Introduction (30 seconds)**

**Say**: 
> "Akash Autopilot is an autonomous AI agent that runs entirely on Akash Network. It continuously monitors deployments, uses AkashML for intelligent decision-making, and automatically scales or redeploys services based on policy guardrails."

**Show**:
- Akash Console showing your deployment
- Mention it's running on decentralized infrastructure

---

### **Part 2: Live Agent Status (45 seconds)**

**Navigate to**: `https://<your-deployment-url>/status`

**Say**:
> "The agent is running continuously. Let's check its status."

**Point out**:
```json
{
  "running": true,
  "loop_count": 47,          // ← Shows it's been running autonomously
  "last_loop_time": "2026-02-21T12:45:00",
  "database_stats": {
    "total_actions": 12,
    "actions_last_hour": 3,
    "tracked_deployments": 2
  }
}
```

**Say**:
> "The agent has completed 47 decision cycles. It's tracking 2 deployments and has executed 12 actions total, with 3 in the last hour."

---

### **Part 3: Action Audit Trail (45 seconds)**

**Navigate to**: `https://<your-deployment-url>/actions`

**Say**:
> "Every action is logged with timestamps and reasoning. This is our verifiable audit trail."

**Show action log**:
```json
{
  "actions": [
    {
      "id": 12,
      "timestamp": "2026-02-21T12:30:00",
      "action_type": "scale",
      "deployment_id": "12345",
      "details": "{\"new_count\": 2, \"reason\": \"High CPU usage detected\"}",
      "status": "completed"
    },
    {
      "id": 11,
      "timestamp": "2026-02-21T12:15:00",
      "action_type": "no_action",
      "status": "completed"
    }
  ]
}
```

**Say**:
> "Here we see the agent scaled a deployment to 2 replicas due to high CPU usage. Notice: timestamp, reason from AI, and completion status."

---

### **Part 4: Policy Guardrails (30 seconds)**

**Navigate to**: `https://<your-deployment-url>/policy`

**Say**:
> "The agent isn't reckless. It follows strict policy guardrails to prevent unsafe actions."

**Show policy**:
```json
{
  "rate_limits": {
    "max_actions_per_hour": 10,
    "max_actions_per_day": 50
  },
  "cooldowns": {
    "scale_cooldown_seconds": 3600,
    "redeploy_cooldown_seconds": 7200
  },
  "constraints": {
    "max_replicas": 10,
    "min_replicas": 0
  }
}
```

**Say**:
> "Rate limits prevent spam. Cooldowns prevent thrashing. Constraints prevent bad scaling decisions."

---

### **Part 5: Restart Resilience (30 seconds)**

**Say**:
> "Now the magic part: persistence. Watch what happens when I restart the container."

**Actions**:
1. In Akash Console, redeploy the service (or kill/restart via CLI)
2. Wait ~10 seconds for restart
3. Refresh `/status` endpoint

**Show**:
```json
{
  "running": true,
  "loop_count": 1,              // ← Reset (new container)
  "database_stats": {
    "total_actions": 12,        // ← PERSISTED!
    "actions_last_hour": 3,     // ← PERSISTED!
    "tracked_deployments": 2    // ← PERSISTED!
  }
}
```

**Say**:
> "New container, but all historical data persisted! The action ledger, deployment states, and cooldowns survived the restart. This is true stateful autonomy."

---

## 🎭 Optional Advanced Demos

### Show AI Reasoning

**Navigate to recent action details**:
```bash
curl https://<your-deployment-url>/actions | jq '.actions[0].details' | jq -r
```

**Show**:
```json
{
  "new_count": 2,
  "reason": "CPU usage at 85% for 5 minutes. Scaling to 2 replicas to handle load."
}
```

**Say**:
> "This reasoning came from AkashML (Llama 3.3 70B). The AI analyzed metrics and recommended this action."

---

### Show Deployment Tracking

**Navigate to**: `https://<your-deployment-url>/deployments`

**Show**:
```json
{
  "deployments": [
    {
      "deployment_id": "12345",
      "name": "web-service",
      "status": "active",
      "replicas": 2,
      "last_checked": "2026-02-21T12:45:00",
      "metrics": "{\"cpu_usage\": 45, \"memory_usage\": 60}"
    }
  ]
}
```

**Say**:
> "The agent tracks deployment health. These metrics inform AI decisions."

---

## 🚨 Troubleshooting During Demo

### If agent seems stuck

**Check**:
```bash
curl https://<your-deployment-url>/status
```

Look at `last_loop_time` - should be recent (< 2 minutes old)

**Fallback**: 
> "The agent runs every 120 seconds. Let's check recent actions instead." → Navigate to `/actions`

---

### If no actions showing

**Explain**:
> "The AI is conservative. It only acts when truly necessary. No action is often the right action."

**Show**:
```bash
curl https://<your-deployment-url>/actions | jq '.actions[] | select(.action_type == "no_action")'
```

**Say**:
> "See these 'no_action' entries? The AI chose to do nothing - which is smart when everything is healthy."

---

### If deployment is down

**Fallback to local demo**:
```bash
# Run locally with mock mode
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e CONSOLE_API_KEY=test \
  -e AKASHML_API_KEY=test \
  your-image:latest

# Then demo endpoints on localhost:8000
```

**Explain**:
> "This is running in mock mode - same code, fake APIs. Shows the architecture works."

---

## 🎯 Key Talking Points

### Why This is Impressive

1. **True Autonomy**: No manual triggers, no cron jobs, no human in the loop
2. **AI-Powered**: Uses AkashML (on Akash) for intelligent reasoning
3. **Production-Ready**: Policy guardrails, audit trails, error handling
4. **Stateful**: Survives restarts with persistent database
5. **Observable**: Rich API for monitoring and verification
6. **Runs on Akash**: Eats its own dog food - agent manages Akash using Akash

### Technical Highlights

- **Stack**: Python, FastAPI, SQLite, AkashML, Console API
- **Architecture**: Event loop + policy engine + LLM reasoning
- **Storage**: Persistent volumes for SQLite database
- **Security**: Non-root user, env-based secrets, rate limits
- **Observability**: 8 REST endpoints for monitoring

---

## 📸 Screenshot Checklist

Before demo, capture these for slides:

1. Akash Console showing deployment
2. `/status` endpoint showing high loop count
3. `/actions` endpoint with real actions
4. `/policy` endpoint showing guardrails
5. Database stats before/after restart

---

## ⏱️ Time Management

| Section | Duration | Cumulative |
|---------|----------|------------|
| Introduction | 30s | 0:30 |
| Agent Status | 45s | 1:15 |
| Action Trail | 45s | 2:00 |
| Policy | 30s | 2:30 |
| Restart Demo | 30s | 3:00 |

Total: **3 minutes**

Add 2 minutes for Q&A = **5 minute presentation**

---

## 🎤 Closing Statement

**Say**:
> "Akash Autopilot demonstrates true autonomous infrastructure management. It's an AI agent that thinks, decides, and acts - all running decentralized on Akash Network. The persistent state, policy guardrails, and complete audit trail make it production-ready. This is the future of autonomous infrastructure."

**Call to action**:
> "All code is open source. Try it yourself: [your-github-repo]"

---

**Good luck with your demo! 🚀**
