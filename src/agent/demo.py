"""Demo mode for testing AI decision-making without real deployments"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


class DemoDeploymentGenerator:
    """Generate realistic demo deployments with various scenarios"""
    
    SCENARIOS = [
        {
            "name": "High CPU Usage",
            "cpu_percent": 85,
            "memory_percent": 45,
            "error_rate": 0.02,
            "expected_action": "scale_up",
            "reasoning": "CPU usage consistently above 80% threshold"
        },
        {
            "name": "Memory Pressure",
            "cpu_percent": 40,
            "memory_percent": 92,
            "error_rate": 0.05,
            "expected_action": "scale_up",
            "reasoning": "Memory usage critical, approaching OOM"
        },
        {
            "name": "High Error Rate",
            "cpu_percent": 30,
            "memory_percent": 50,
            "error_rate": 0.15,
            "expected_action": "redeploy",
            "reasoning": "Error rate exceeds 10% threshold, indicates code issue"
        },
        {
            "name": "Underutilized",
            "cpu_percent": 12,
            "memory_percent": 18,
            "error_rate": 0.001,
            "expected_action": "scale_down",
            "reasoning": "Resource usage below 20%, cost optimization opportunity"
        },
        {
            "name": "Healthy Deployment",
            "cpu_percent": 45,
            "memory_percent": 55,
            "error_rate": 0.001,
            "expected_action": "monitor",
            "reasoning": "All metrics within healthy ranges"
        }
    ]
    
    def __init__(self):
        self.deployment_counter = 0
        self.current_scenario_index = 0
    
    def generate_demo_deployment(self) -> Dict[str, Any]:
        """Generate a demo deployment with realistic metrics"""
        self.deployment_counter += 1
        scenario = self.SCENARIOS[self.current_scenario_index % len(self.SCENARIOS)]
        self.current_scenario_index += 1
        
        deployment_id = f"demo-deployment-{self.deployment_counter}"
        
        # Add some randomness to make it more realistic
        cpu_variance = random.uniform(-5, 5)
        mem_variance = random.uniform(-5, 5)
        
        return {
            "dseq": f"{1000000 + self.deployment_counter}",
            "name": f"demo-app-{scenario['name'].lower().replace(' ', '-')}",
            "owner": "demo-wallet-akash1abc123...",
            "status": "active",
            "replicas": random.randint(2, 5),
            "resources": {
                "cpu": "1000m",
                "memory": "1Gi",
                "storage": "512Mi"
            },
            "metrics": {
                "cpu_percent": max(0, min(100, scenario["cpu_percent"] + cpu_variance)),
                "memory_percent": max(0, min(100, scenario["memory_percent"] + mem_variance)),
                "error_rate": scenario["error_rate"] * random.uniform(0.8, 1.2),
                "requests_per_second": random.randint(100, 1000),
                "response_time_ms": random.randint(50, 500),
                "uptime_hours": random.randint(24, 720)
            },
            "scenario": scenario["name"],
            "expected_action": scenario["expected_action"],
            "scenario_reasoning": scenario["reasoning"],
            "created_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 168))).isoformat()
        }
    
    def generate_multiple_deployments(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple demo deployments"""
        return [self.generate_demo_deployment() for _ in range(count)]
