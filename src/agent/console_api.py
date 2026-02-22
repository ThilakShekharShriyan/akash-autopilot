"""Akash Console API client for deployment management"""

import logging
from typing import Dict, List, Optional
import requests
from src.config import settings

logger = logging.getLogger(__name__)


class ConsoleAPIClient:
    """Client for Akash Console API"""
    
    def __init__(self):
        self.base_url = settings.console_api_base_url
        self.api_key = settings.console_api_key
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        logger.info(f"Console API client initialized: {self.base_url}")
    
    def list_deployments(self) -> Optional[List[Dict]]:
        """List all deployments"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/deployments",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            deployments = data.get("deployments", [])
            logger.info(f"Listed {len(deployments)} deployments")
            return deployments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list deployments: {e}")
            return None
    
    def get_deployment(self, deployment_id: str) -> Optional[Dict]:
        """Get deployment details"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/deployments/{deployment_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            deployment = response.json()
            
            logger.info(f"Retrieved deployment: {deployment_id}")
            return deployment
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get deployment {deployment_id}: {e}")
            return None
    
    def update_deployment(
        self,
        deployment_id: str,
        sdl: str
    ) -> Optional[Dict]:
        """Update deployment with new SDL (for scaling/redeploying)"""
        try:
            response = requests.put(
                f"{self.base_url}/v1/deployments/{deployment_id}",
                headers=self.headers,
                json={"data": {"sdl": sdl}},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Updated deployment: {deployment_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update deployment {deployment_id}: {e}")
            return None
    
    def close_deployment(self, deployment_id: str) -> bool:
        """Close a deployment"""
        try:
            response = requests.delete(
                f"{self.base_url}/v1/deployments/{deployment_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Closed deployment: {deployment_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to close deployment {deployment_id}: {e}")
            return False


class MockConsoleAPIClient:
    """Mock Console API client for testing"""
    
    def list_deployments(self) -> List[Dict]:
        """Return mock deployments"""
        logger.info("Using MOCK Console API client")
        return [
            {
                "dseq": "12345",
                "name": "test-deployment",
                "status": "active",
                "replicas": 1,
                "services": {
                    "web": {
                        "replicas": 1,
                        "image": "nginx:latest"
                    }
                }
            }
        ]
    
    def get_deployment(self, deployment_id: str) -> Dict:
        """Return mock deployment details"""
        return {
            "dseq": deployment_id,
            "name": "test-deployment",
            "status": "active",
            "replicas": 1,
            "services": {
                "web": {
                    "replicas": 1,
                    "image": "nginx:latest",
                    "resources": {
                        "cpu": "0.5",
                        "memory": "512Mi"
                    }
                }
            },
            "metrics": {
                "cpu_usage": 45,
                "memory_usage": 60,
                "uptime_seconds": 3600
            }
        }
    
    def update_deployment(self, deployment_id: str, sdl: str) -> Dict:
        """Mock update deployment"""
        logger.info(f"MOCK: Updated deployment {deployment_id}")
        return {"success": True, "deployment_id": deployment_id}
    
    def close_deployment(self, deployment_id: str) -> bool:
        """Mock close deployment"""
        logger.info(f"MOCK: Closed deployment {deployment_id}")
        return True


def get_console_client(use_mock: bool = False) -> ConsoleAPIClient:
    """Factory function to get Console API client"""
    if use_mock:
        return MockConsoleAPIClient()
    return ConsoleAPIClient()
