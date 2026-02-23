"""FastAPI server with monitoring endpoints"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from src.agent.loop import AutopilotAgent
from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[AutopilotAgent] = None
agent_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global agent, agent_task
    
    # Startup
    logger.info("Starting Akash Autopilot...")
    
    # Check if running in mock mode (for local testing without API keys)
    use_mock = False
    try:
        # Test if API keys are placeholder values
        if (settings.console_api_key.startswith("your_") or 
            settings.akashml_api_key.startswith("your_")):
            logger.warning("Using MOCK mode - API keys are placeholders")
            use_mock = True
    except Exception:
        logger.warning("Using MOCK mode - missing API keys")
        use_mock = True
    
    agent = AutopilotAgent(use_mock_apis=use_mock)
    await agent.initialize()
    
    # Start agent loop in background
    agent_task = asyncio.create_task(agent.run_loop())
    logger.info("Agent loop started")
    
    yield
    
    # Shutdown
    logger.info("Stopping Akash Autopilot...")
    if agent:
        await agent.shutdown()
    if agent_task:
        agent_task.cancel()
        try:
            await agent_task
        except asyncio.CancelledError:
            pass
    logger.info("Shutdown complete")


app = FastAPI(
    title="Akash Autopilot",
    description="Autonomous Infrastructure Operator for Akash Network",
    version="0.1.0",
    lifespan=lifespan
)


# ===== MODELS =====

class HealthResponse(BaseModel):
    status: str
    timestamp: str


class StatusResponse(BaseModel):
    running: bool
    loop_count: int
    last_loop_time: Optional[str]
    database_stats: dict
    configuration: dict


# ===== ENDPOINTS =====

@app.get("/")
async def root():
    """Serve the frontend dashboard"""
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    # Fallback to API info if frontend not found
    return {
        "name": "Akash Autopilot",
        "version": "0.1.0",
        "description": "Autonomous Infrastructure Operator",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "actions": "/actions",
            "deployments": "/deployments",
            "policy": "/policy",
            "stats": "/stats"
        }
    }

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Akash Autopilot",
        "version": "0.1.0",
        "description": "Autonomous Infrastructure Operator",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "actions": "/actions",
            "deployments": "/deployments",
            "policy": "/policy",
            "stats": "/stats"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for Akash provider monitoring"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/status", response_model=StatusResponse)
async def status():
    """Get current agent status"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return await agent.get_status()


@app.get("/actions")
async def get_actions(limit: int = 50):
    """Get recent actions from audit ledger"""
    if not agent or not agent.db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    actions = await agent.db.get_recent_actions(limit=limit)
    return {
        "total": len(actions),
        "actions": actions
    }


@app.get("/actions/{action_type}")
async def get_actions_by_type(action_type: str, limit: int = 50):
    """Get actions of specific type"""
    if not agent or not agent.db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    actions = await agent.db.get_actions_by_type(action_type, limit=limit)
    return {
        "action_type": action_type,
        "total": len(actions),
        "actions": actions
    }


@app.get("/deployments")
async def get_deployments():
    """Get tracked deployment states"""
    if not agent or not agent.db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    deployments = await agent.db.get_all_deployments()
    return {
        "total": len(deployments),
        "deployments": deployments
    }


@app.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get specific deployment state"""
    if not agent or not agent.db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    deployment = await agent.db.get_deployment_state(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return deployment


@app.get("/policy")
async def get_policy():
    """Get current policy settings"""
    if not agent or not agent.policy:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    policy_summary = await agent.policy.get_policy_summary()
    return policy_summary


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    if not agent or not agent.db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    stats = await agent.db.get_stats()
    return stats


# ===== ERROR HANDLERS =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower()
    )
