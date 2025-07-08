import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class OpenSearchSettings(BaseSettings):
    """Configuration for OpenSearch connection."""
    model_config = SettingsConfigDict(env_prefix='OPENSEARCH_')
    
    host: str = "http://localhost:9200"
    user: str = "admin"
    password: str = Field(..., repr=False) # Use Field to hide password from logs
    embedding_model_name: str = "all-MiniLM-L6-v2"
    index_name: str = "adk-docs-index"

class Settings(BaseSettings):
    """Manages all application configuration."""
    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')

    gemini_api_key: str = Field(..., repr=False)
    llm_model_name: str = "gemini-2.0-flash"
    server_title: str = "Google ADK Agent Code Generator (RAG-Powered)"
    server_version: str = "0.0.1"

    # Nested OpenSearch settings
    opensearch: OpenSearchSettings = OpenSearchSettings()


settings = Settings()