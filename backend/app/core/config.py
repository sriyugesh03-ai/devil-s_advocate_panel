from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Devil's Advocate Panel"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8999
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = "groq"  # "groq" (fast 120b) or "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # MCP (Model Context Protocol) Settings
    TAVILY_API_KEY: str = ""
    GITHUB_PERSONAL_ACCESS_TOKEN: str = ""

    # LangSmith Tracing
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "devils-advocate-panel"

    # Database (MongoDB Atlas)
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGO_DB_URL: str = ""
    MONGODB_DB_NAME: str = "devils_advocate"

    # Authentication (Clerk)
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_ISSUER: str = ""
    APP_JWT_SECRET: str = ""
    COOKIE_SECURE: bool = False

    # Vector Storage
    VECTOR_STORE_PATH: str = "./data/vectorstore"

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def effective_mongodb_uri(self) -> str:
        if self.MONGO_DB_URL and self.MONGO_DB_URL.strip():
            return self.MONGO_DB_URL.strip()
        return self.MONGODB_URI.strip()

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
