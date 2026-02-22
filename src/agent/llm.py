"""AkashML integration for AI reasoning"""

import json
import logging
from typing import Dict, Optional
from openai import AsyncOpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class AkashMLClient:
    """Client for AkashML reasoning service"""
    
    SYSTEM_PROMPT = """You are an autonomous infrastructure operator for Akash Network deployments.

Your role is to analyze deployment health metrics and recommend actions to maintain optimal performance.

You must respond with ONLY valid JSON in this exact format:
{
  "reasoning": "Brief explanation of your analysis",
  "actions": [
    {
      "type": "scale|redeploy|no_action",
      "deployment_id": "deployment_id_here",
      "new_count": 2,
      "reason": "Why this action is needed"
    }
  ]
}

Guidelines:
- Only recommend actions when truly necessary
- "no_action" is a valid and often correct choice
- Scaling up: Only if metrics show resource pressure
- Scaling down: Only if utilization is very low for extended periods
- Redeploy: Only for critical issues that restart can fix
- Never recommend more than 2 actions at once
- Always provide clear reasoning

Available action types:
- "scale": Change replica count (requires: deployment_id, new_count)
- "redeploy": Restart deployment (requires: deployment_id)
- "no_action": Do nothing (no additional fields needed)

Current policy constraints:
- Maximum 10 replicas per deployment
- Minimum 0 replicas (for shutdown)
- Actions have cooldown periods to prevent thrashing
"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.akashml_base_url,
            api_key=settings.akashml_api_key
        )
        self.model = settings.akashml_model
        logger.info(f"AkashML client initialized with model: {self.model}")
    
    async def get_decision(
        self,
        deployments: list[Dict],
        policy_summary: Dict,
        recent_actions: list[Dict]
    ) -> Optional[Dict]:
        """
        Get AI decision based on current state
        
        Args:
            deployments: List of deployment states with metrics
            policy_summary: Current policy constraints
            recent_actions: Recent action history for context
        
        Returns:
            Action plan dict or None if error
        """
        
        # Build context prompt
        user_prompt = self._build_context_prompt(
            deployments,
            policy_summary,
            recent_actions
        )
        
        try:
            logger.info("Requesting decision from AkashML...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent decisions
                max_tokens=1000,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Parse response
            content = response.choices[0].message.content
            action_plan = json.loads(content)
            
            logger.info(f"AkashML decision received: {action_plan.get('reasoning', 'N/A')}")
            logger.debug(f"Full action plan: {json.dumps(action_plan, indent=2)}")
            
            return action_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AkashML response as JSON: {e}")
            logger.error(f"Response content: {content}")
            return None
        
        except Exception as e:
            logger.error(f"AkashML request failed: {e}")
            return None
    
    def _build_context_prompt(
        self,
        deployments: list[Dict],
        policy_summary: Dict,
        recent_actions: list[Dict]
    ) -> str:
        """Build context prompt for LLM"""
        
        prompt_parts = []
        
        # Current deployments state
        prompt_parts.append("=== CURRENT DEPLOYMENTS ===")
        if deployments:
            for dep in deployments:
                metrics = json.loads(dep.get("metrics", "{}")) if dep.get("metrics") else {}
                prompt_parts.append(f"""
Deployment: {dep.get('name', 'unknown')}
ID: {dep.get('deployment_id')}
Status: {dep.get('status')}
Current Replicas: {dep.get('replicas', 0)}
Last Checked: {dep.get('last_checked')}
Metrics: {json.dumps(metrics, indent=2) if metrics else 'No metrics available'}
""")
        else:
            prompt_parts.append("No deployments currently tracked.")
        
        # Policy constraints
        prompt_parts.append("\n=== POLICY CONSTRAINTS ===")
        prompt_parts.append(json.dumps(policy_summary, indent=2))
        
        # Recent actions context
        prompt_parts.append("\n=== RECENT ACTIONS (Last 10) ===")
        if recent_actions:
            for action in recent_actions[:10]:
                details = json.loads(action.get("details", "{}")) if action.get("details") else {}
                prompt_parts.append(
                    f"- {action.get('timestamp')}: {action.get('action_type')} "
                    f"[{action.get('status')}] - {details.get('reason', 'N/A')}"
                )
        else:
            prompt_parts.append("No recent actions.")
        
        prompt_parts.append("\n=== YOUR TASK ===")
        prompt_parts.append(
            "Analyze the deployment states and metrics above. "
            "Determine if any actions are needed to maintain optimal performance. "
            "Remember: doing nothing is often the right choice. "
            "Only recommend actions when metrics clearly indicate a need."
        )
        
        return "\n".join(prompt_parts)


class MockAkashMLClient:
    """Mock client for testing without AkashML access"""
    
    async def get_decision(
        self,
        deployments: list[Dict],
        policy_summary: Dict,
        recent_actions: list[Dict]
    ) -> Dict:
        """Return mock decision (always no action)"""
        logger.info("Using MOCK AkashML client (returns no_action)")
        
        return {
            "reasoning": "Mock client - no action taken",
            "actions": [
                {
                    "type": "no_action"
                }
            ]
        }
