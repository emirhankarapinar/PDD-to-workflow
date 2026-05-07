"""
PDD Forge - Core Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "PDD Forge"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # LLM
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    llm_mock: bool = True  # Use mock responses if no API key
    
    # PDF Processing
    max_pdf_pages: int = 100
    max_file_size_mb: int = 50
    
    # Templates
    template_dir: str = "templates"
    default_template: str = "reframework-queue"
    
    # Output
    output_dir: str = "output"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
