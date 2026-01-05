"""Application configuration management"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = Field(default="EagleEye", env="APP_NAME")
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # File Upload
    max_upload_size: int = Field(default=104857600, env="MAX_UPLOAD_SIZE")  # 100MB
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    allowed_extensions: str = Field(
        default="pdf,docx,doc,txt",
        env="ALLOWED_EXTENSIONS"
    )
    
    def get_allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    # Security & Compliance
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
    data_retention_hours: int = Field(default=24, env="DATA_RETENTION_HOURS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
