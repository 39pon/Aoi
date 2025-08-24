# =============================================================================
# Aoi Core Agent - Configuration Management
# =============================================================================

import os
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
# Try to load from current directory first, then parent directories
load_dotenv(find_dotenv())


class AoiConfig(BaseModel):
    """
    Configuration management for Aoi Core Agent.
    
    This class handles all configuration settings for the Aoi agent,
    including API keys, service endpoints, and operational parameters.
    """
    
    # =============================================================================
    # Core Service Configuration
    # =============================================================================
    
    # Agent Configuration
    agent_name: str = Field(default=os.getenv("AOI_AGENT_NAME", "Aoi"))
    agent_version: str = Field(default=os.getenv("AOI_AGENT_VERSION", "0.1.0"))
    debug_mode: bool = Field(default=os.getenv("AOI_DEBUG", "False").lower() == "true")
    
    # API Configuration
    api_host: str = Field(default=os.getenv("AOI_API_HOST", "0.0.0.0"))
    api_port: int = Field(default=int(os.getenv("AOI_API_PORT", "8000")))
    api_workers: int = Field(default=int(os.getenv("AOI_API_WORKERS", "1")))
    
    # =============================================================================
    # External API Keys
    # =============================================================================
    
    # Google Gemini API
    google_api_key: Optional[str] = Field(default=os.getenv("GOOGLE_API_KEY"))
    gemini_model: str = Field(default=os.getenv("GEMINI_MODEL", "gemini-pro"))
    
    # Jina AI API
    jina_api_key: Optional[str] = Field(default=os.getenv("JINA_API_KEY"))
    jina_embedding_model: str = Field(default=os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v2-base-en"))
    
    # OpenAI API (Optional)
    openai_api_key: Optional[str] = Field(
        default=None, env="OPENAI_API_KEY"
    )
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # =============================================================================
    # Database Configuration
    # =============================================================================
    
    # Weaviate Vector Database
    weaviate_host: str = Field(default="localhost", env="WEAVIATE_HOST")
    weaviate_port: int = Field(default=8080, env="WEAVIATE_PORT")
    weaviate_grpc_port: int = Field(
        default=50051, env="WEAVIATE_GRPC_PORT"
    )
    weaviate_scheme: str = Field(default="http", env="WEAVIATE_SCHEME")
    
    # Redis Session Storage
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(
        default=None, env="REDIS_PASSWORD"
    )
    
    # =============================================================================
    # Knowledge Base Configuration
    # =============================================================================
    
    # Obsidian Integration
    obsidian_vault_path: str = Field(
        default="./obsidian-data", env="OBSIDIAN_VAULT_PATH"
    )
    obsidian_auto_sync: bool = Field(default=True, env="OBSIDIAN_AUTO_SYNC")
    obsidian_sync_interval: int = Field(
        default=300, env="OBSIDIAN_SYNC_INTERVAL"
    )
    
    # =============================================================================
    # Security Configuration
    # =============================================================================
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production", env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(
        default=24, env="JWT_EXPIRATION_HOURS"
    )
    
    # CORS Configuration
    cors_origins: list = Field(
        default=["http://localhost:3000"], env="CORS_ORIGINS"
    )
    
    # =============================================================================
    # Logging Configuration
    # =============================================================================
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # =============================================================================
    # Performance Configuration
    # =============================================================================
    
    # Memory Management
    max_memory_entries: int = Field(
        default=10000, env="MAX_MEMORY_ENTRIES"
    )
    memory_cleanup_interval: int = Field(
        default=3600, env="MEMORY_CLEANUP_INTERVAL"
    )
    
    # Request Limits
    max_request_size: int = Field(
        default=10485760, env="MAX_REQUEST_SIZE"
    )  # 10MB
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Debug: Print API key status
        print(f"Debug - google_api_key loaded: {self.google_api_key is not None}")
        print(f"Debug - jina_api_key loaded: {self.jina_api_key is not None}")
        if self.google_api_key:
            print(f"Debug - google_api_key starts with: {self.google_api_key[:10]}...")
        if self.jina_api_key:
            print(f"Debug - jina_api_key starts with: {self.jina_api_key[:10]}...")
    
    @property
    def weaviate_url(self) -> str:
        """Get the complete Weaviate URL."""
        return f"{self.weaviate_scheme}://{self.weaviate_host}:{self.weaviate_port}"
    
    @property
    def redis_url(self) -> str:
        """Get the complete Redis URL."""
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@{self.redis_host}:"
                f"{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def validate_required_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        return {
            "google_api_key": self.google_api_key is not None,
            "jina_api_key": self.jina_api_key is not None,
        }
    
    def get_missing_keys(self) -> list[str]:
        """Get list of missing required API keys."""
        validation = self.validate_required_keys()
        return [
            key for key, is_valid in validation.items() if not is_valid
        ]


# Global configuration instance
config = AoiConfig()