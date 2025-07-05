import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "ThirdPartyRiskPortal"
    app_version: str = "1.0.0"
    debug: bool = True  # Temporarily enabled for development
    
    # Database
    database_url: str = "postgresql://tprm_user:tprm_password@localhost:5432/tprm_db"
    
    # Individual database components for flexibility
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tprm_db"
    db_user: str = "tprm_user"
    db_password: str = "tprm_password"  # Change this in production!
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Azure Storage
    azure_storage_connection_string: Optional[str] = None
    azure_storage_account_name: Optional[str] = None
    azure_storage_account_key: Optional[str] = None
    azure_storage_container_name: str = "tprm-documents"
    
    # Azure Key Vault
    azure_key_vault_url: Optional[str] = None
    
    # Azure Application Insights
    azure_application_insights_connection_string: Optional[str] = None
    
    # Dapr
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001
    dapr_enabled: bool = True
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # File Upload
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "image/jpeg",
        "image/png"
    ]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"
elif os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.log_level = "DEBUG"
