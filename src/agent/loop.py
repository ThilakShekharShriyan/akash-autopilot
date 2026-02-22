"""Main autonomous agent loop"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from src.config import settings
from src.database.db import AutopilotDB
from src.agent.policy import PolicyGuardrails, ActionValidator
from src.agent.llm import AkashMLClient
from src.agent.console_api import get_console_client

logger = logging.getLogger(__name__)


class AutopilotAgent:
    """Autonomous agent for Akash infrastructure management"""
    
    def __init__(self, use_mock_apis: bool = False):
        self.db: Optional[AutopilotDB] = None
        self.policy: Optional[PolicyGuardrails] = None
        self.llm_client: Optional[AkashMLClient] = None
        self.console_client = get_console_client(use_mock=use_mock_apis)
        self.running = False
        self.last_loop_time: Optional[datetime] = None
        self.loop_count = 0
        self.use_mock_apis = use_mock_apis
        
    async def initialize(self):
        """Initialize agent components"""
        logger.info("Initializing Akash Autopilot Agent...")
        
        # Initialize database
        self.db = AutopilotDB(settings.db_path)
        await self.db.connect()
        
        # Initialize policy guardrails
        self.policy = PolicyGuardrails(self.db)
        
        # Initialize LLM client
        if not self.use_mock_apis:
            self.llm_client = AkashMLClient()
        else:
            from src.agent.llm import MockAkashMLClient
            self.llm_client = MockAkashMLClient()
        
        logger.info("Agent initialization complete")
    
    async def shutdown(self):
        """Cleanup and shutdown"""
        logger.info("Shutting down agent...")
        self.running = False
        
        if self.db:
            await self.db.close()
        
        logger.info("Agent shutdown complete")
    
    async def run_loop(self):
        """Run the main autonomous loop"""
        self.running = True
        logger.info(f"Starting autonomous loop (interval: {settings.loop_interval}s)")
        
        while self.running:
            try:
                await self._execute_loop_iteration()
                self.loop_count += 1
                self.last_loop_time = datetime.utcnow()
                
                # Wait for next iteration
                logger.info(f"Loop #{self.loop_count} complete. Sleeping {settings.loop_interval}s...")
                await asyncio.sleep(settings.loop_interval)
                
            except asyncio.CancelledError:
                logger.info("Loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in agent loop: {e}", exc_info=True)
                # Continue running despite errors
                await asyncio.sleep(settings.loop_interval)
    
    async def _execute_loop_iteration(self):
        """Execute one iteration of the agent loop"""
        logger.info("=" * 60)
        logger.info(f"Agent Loop Iteration #{self.loop_count + 1}")
        logger.info("=" * 60)
        
        # Step 1: Cleanup expired cooldowns
        await self.db.cleanup_expired_cooldowns()
        
        # Step 2: Fetch deployment states
        deployments = await self._fetch_deployments()
        logger.info(f"Fetched {len(deployments)} deployment(s)")
        
        # Step 3: Get policy summary
        policy_summary = await self.policy.get_policy_summary()
        
        # Step 4: Get recent actions for context
        recent_actions = await self.db.get_recent_actions(limit=10)
        
        # Step 5: Get decision from AkashML
        action_plan = await self.llm_client.get_decision(
            deployments=deployments,
            policy_summary=policy_summary,
            recent_actions=recent_actions
        )
        
        if not action_plan:
            logger.warning("No action plan received from LLM")
            return
        
        # Step 6: Validate action plan structure
        is_valid, error = ActionValidator.validate_action_plan(action_plan)
        if not is_valid:
            logger.error(f"Invalid action plan: {error}")
            await self.db.log_action(
                action_type="validation_failed",
                details={"error": error, "plan": action_plan},
                status="failed"
            )
            return
        
        # Step 7: Extract and sanitize actions
        actions = ActionValidator.sanitize_action_plan(action_plan)
        logger.info(f"Received {len(actions)} action(s) from LLM")
        
        # Step 8: Execute each action
        for action in actions:
            await self._execute_action(action)
    
    async def _fetch_deployments(self) -> list[dict]:
        """Fetch current deployment states"""
        deployments_data = []
        
        # Get deployments from Console API
        api_deployments = self.console_client.list_deployments()
        
        if not api_deployments:
            logger.warning("No deployments returned from Console API")
            # Return cached deployments from DB
            cached = await self.db.get_all_deployments()
            return cached
        
        # Update database with current state
        for dep in api_deployments:
            deployment_id = dep.get("dseq", dep.get("id", "unknown"))
            name = dep.get("name", "unnamed")
            status = dep.get("status", "unknown")
            
            # Extract replica count from services
            replicas = self._get_replica_count(dep)
            
            # Get detailed metrics if available
            metrics = dep.get("metrics", {})
            
            # Update DB
            await self.db.update_deployment_state(
                deployment_id=deployment_id,
                name=name,
                status=status,
                replicas=replicas,
                metrics=metrics
            )
            
            deployments_data.append({
                "deployment_id": deployment_id,
                "name": name,
                "status": status,
                "replicas": replicas,
                "metrics": metrics,
                "last_checked": datetime.utcnow().isoformat()
            })
        
        return deployments_data
    
    def _get_replica_count(self, deployment: dict) -> int:
        """Extract total replica count from deployment"""
        services = deployment.get("services", {})
        total_replicas = 0
        
        for service_name, service_config in services.items():
            replicas = service_config.get("replicas", 1)
            total_replicas += replicas
        
        return total_replicas
    
    async def _execute_action(self, action: dict):
        """Execute a single action with policy validation"""
        action_type = action["type"]
        deployment_id = action.get("deployment_id")
        details = action.get("details", {})
        
        logger.info(f"Attempting action: {action_type} on {deployment_id}")
        
        # Log action initiation
        action_id = await self.db.log_action(
            action_type=action_type,
            deployment_id=deployment_id,
            details=details,
            status="pending"
        )
        
        # Validate against policy
        is_allowed, reason = await self.policy.validate_action(
            action_type=action_type,
            deployment_id=deployment_id,
            details=details
        )
        
        if not is_allowed:
            logger.warning(f"Action blocked by policy: {reason}")
            await self.db.update_action_status(
                action_id=action_id,
                status="blocked",
                error=reason
            )
            return
        
        # Execute action based on type
        success = False
        error = None
        
        try:
            if action_type == "scale":
                success = await self._execute_scale(deployment_id, details)
            elif action_type == "redeploy":
                success = await self._execute_redeploy(deployment_id, details)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                error = f"Unknown action type: {action_type}"
        
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            error = str(e)
        
        # Update action status
        final_status = "completed" if success else "failed"
        await self.db.update_action_status(
            action_id=action_id,
            status=final_status,
            error=error
        )
        
        # Apply cooldown if successful
        if success:
            await self.policy.apply_cooldown(action_type, deployment_id)
        
        logger.info(f"Action {action_type} {final_status}")
    
    async def _execute_scale(self, deployment_id: str, details: dict) -> bool:
        """Execute scaling action"""
        new_count = details.get("new_count")
        reason = details.get("reason", "LLM recommendation")
        
        logger.info(f"Scaling deployment {deployment_id} to {new_count} replicas")
        logger.info(f"Reason: {reason}")
        
        # Get current deployment
        deployment = self.console_client.get_deployment(deployment_id)
        if not deployment:
            logger.error(f"Deployment {deployment_id} not found")
            return False
        
        # TODO: Modify SDL to update replica count
        # This requires SDL parsing and modification
        # For MVP, we'll log the action but not implement the actual scaling
        
        logger.warning("SDL modification not yet implemented - action logged only")
        return True  # Return True to demonstrate the flow
    
    async def _execute_redeploy(self, deployment_id: str, details: dict) -> bool:
        """Execute redeploy action"""
        reason = details.get("reason", "LLM recommendation")
        
        logger.info(f"Redeploying deployment {deployment_id}")
        logger.info(f"Reason: {reason}")
        
        # Get current deployment
        deployment = self.console_client.get_deployment(deployment_id)
        if not deployment:
            logger.error(f"Deployment {deployment_id} not found")
            return False
        
        # TODO: Trigger redeploy via Console API
        # This requires updating deployment with same SDL or trigger restart endpoint
        # For MVP, we'll log the action
        
        logger.warning("Redeploy not yet implemented - action logged only")
        return True  # Return True to demonstrate the flow
    
    async def get_status(self) -> dict:
        """Get current agent status"""
        stats = await self.db.get_stats() if self.db else {}
        
        return {
            "running": self.running,
            "loop_count": self.loop_count,
            "last_loop_time": self.last_loop_time.isoformat() if self.last_loop_time else None,
            "database_stats": stats,
            "configuration": {
                "loop_interval": settings.loop_interval,
                "db_path": settings.db_path,
                "use_mock_apis": self.use_mock_apis
            }
        }
