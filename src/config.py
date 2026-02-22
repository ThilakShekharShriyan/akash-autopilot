"""Configuration management using pydantic-settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # Akash Console API
    console_api_key: str
    console_api_base_url: str = "https://console-api.akash.network"
    
    # AkashML
    akashml_api_key: str
    akashml_base_url: str = "https://api.akashml.com/v1"
    akashml_model: str = "llama-3-3-70b"
    
    # Agent Configuration
    loop_interval: int = 120
    db_path: str = "/data/autopilot.db"
    
    # Policy Guardrails
    max_actions_per_hour: int = 10
    max_actions_per_day: int = 50
    scale_cooldown_seconds: int = 3600
    redeploy_cooldown_seconds: int = 7200
    
    # Logging
    log_level: str = "INFO"


# Global settings instance
settings = Settings()
