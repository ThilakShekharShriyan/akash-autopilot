"""Policy guardrails for safe autonomous operations"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.config import settings
from src.database.db import AutopilotDB

logger = logging.getLogger(__name__)


class PolicyGuardrails:
    """Enforce policy rules on agent actions"""
    
    def __init__(self, db: AutopilotDB):
        self.db = db
        
    async def validate_action(
        self,
        action_type: str,
        deployment_id: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if an action is allowed by policy
        Returns: (is_allowed, reason_if_not_allowed)
        """
        
        # Check rate limits
        if not await self._check_rate_limits(action_type):
            return False, f"Rate limit exceeded for {action_type}"
        
        # Check cooldowns
        if await self.db.check_cooldown(action_type, deployment_id):
            return False, f"Action {action_type} is in cooldown period"
        
        # Validate action-specific rules
        if action_type == "scale":
            is_valid, reason = await self._validate_scale_action(details)
            if not is_valid:
                return False, reason
        
        elif action_type == "redeploy":
            is_valid, reason = await self._validate_redeploy_action(deployment_id)
            if not is_valid:
                return False, reason
        
        return True, None
    
    async def _check_rate_limits(self, action_type: str) -> bool:
        """Check if rate limits are exceeded"""
        
        # Check hourly limit
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        count_hour = await self.db.count_actions_since(one_hour_ago, action_type)
        
        if count_hour >= settings.max_actions_per_hour:
            logger.warning(
                f"Hourly rate limit exceeded for {action_type}: "
                f"{count_hour}/{settings.max_actions_per_hour}"
            )
            return False
        
        # Check daily limit
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        count_day = await self.db.count_actions_since(one_day_ago, action_type)
        
        if count_day >= settings.max_actions_per_day:
            logger.warning(
                f"Daily rate limit exceeded for {action_type}: "
                f"{count_day}/{settings.max_actions_per_day}"
            )
            return False
        
        return True
    
    async def _validate_scale_action(self, details: Optional[Dict]) -> tuple[bool, Optional[str]]:
        """Validate scaling action parameters"""
        if not details:
            return False, "Scale action requires details"
        
        new_count = details.get("new_count")
        if new_count is None:
            return False, "Scale action requires new_count parameter"
        
        # Ensure reasonable scaling limits
        if new_count < 0:
            return False, "Replica count cannot be negative"
        
        if new_count > 10:  # Max replicas safety limit
            return False, f"Replica count too high: {new_count} (max: 10)"
        
        return True, None
    
    async def _validate_redeploy_action(self, deployment_id: Optional[str]) -> tuple[bool, Optional[str]]:
        """Validate redeploy action"""
        if not deployment_id:
            return False, "Redeploy action requires deployment_id"
        
        # Check if deployment exists in our tracking
        deployment = await self.db.get_deployment_state(deployment_id)
        if not deployment:
            logger.warning(f"Attempting to redeploy unknown deployment: {deployment_id}")
            # Allow it, but log warning
        
        return True, None
    
    async def apply_cooldown(self, action_type: str, deployment_id: Optional[str] = None):
        """Apply cooldown period after action execution"""
        
        # Get cooldown duration based on action type
        cooldown_seconds = {
            "scale": settings.scale_cooldown_seconds,
            "redeploy": settings.redeploy_cooldown_seconds,
        }.get(action_type, 3600)  # Default 1 hour
        
        await self.db.set_cooldown(action_type, cooldown_seconds, deployment_id)
        logger.info(f"Cooldown applied: {action_type} for {cooldown_seconds}s")
    
    async def get_policy_summary(self) -> Dict:
        """Get summary of current policy settings"""
        return {
            "rate_limits": {
                "max_actions_per_hour": settings.max_actions_per_hour,
                "max_actions_per_day": settings.max_actions_per_day,
            },
            "cooldowns": {
                "scale_cooldown_seconds": settings.scale_cooldown_seconds,
                "redeploy_cooldown_seconds": settings.redeploy_cooldown_seconds,
            },
            "constraints": {
                "max_replicas": 10,
                "min_replicas": 0,
            }
        }


class ActionValidator:
    """Helper class to validate LLM-generated actions"""
    
    VALID_ACTION_TYPES = {"scale", "redeploy", "no_action"}
    
    @staticmethod
    def validate_action_plan(action_plan: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate action plan structure from LLM
        Returns: (is_valid, error_message)
        """
        
        if not isinstance(action_plan, dict):
            return False, "Action plan must be a dictionary"
        
        if "actions" not in action_plan:
            return False, "Action plan must contain 'actions' key"
        
        actions = action_plan["actions"]
        if not isinstance(actions, list):
            return False, "'actions' must be a list"
        
        # Validate each action
        for i, action in enumerate(actions):
            if not isinstance(action, dict):
                return False, f"Action {i} must be a dictionary"
            
            if "type" not in action:
                return False, f"Action {i} missing 'type' field"
            
            action_type = action["type"]
            if action_type not in ActionValidator.VALID_ACTION_TYPES:
                return False, (
                    f"Invalid action type: '{action_type}'. "
                    f"Must be one of {ActionValidator.VALID_ACTION_TYPES}"
                )
            
            # Validate type-specific requirements
            if action_type == "scale":
                if "deployment_id" not in action:
                    return False, f"Scale action {i} missing 'deployment_id'"
                if "new_count" not in action:
                    return False, f"Scale action {i} missing 'new_count'"
            
            elif action_type == "redeploy":
                if "deployment_id" not in action:
                    return False, f"Redeploy action {i} missing 'deployment_id'"
        
        return True, None
    
    @staticmethod
    def sanitize_action_plan(action_plan: Dict) -> List[Dict]:
        """Extract and sanitize actions from plan"""
        actions = action_plan.get("actions", [])
        sanitized = []
        
        for action in actions:
            if action.get("type") == "no_action":
                continue
            
            sanitized_action = {
                "type": action["type"],
                "deployment_id": action.get("deployment_id"),
                "details": {}
            }
            
            # Add type-specific fields
            if action["type"] == "scale":
                sanitized_action["details"]["new_count"] = action.get("new_count")
                sanitized_action["details"]["reason"] = action.get("reason", "LLM recommendation")
            
            elif action["type"] == "redeploy":
                sanitized_action["details"]["reason"] = action.get("reason", "LLM recommendation")
            
            sanitized.append(sanitized_action)
        
        return sanitized
