from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Little Desk"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./little_desk.db"
    
    # Ollama Local LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "poolside"
    
    # IMAP Configuration
    IMAP_SERVER: str = ""
    IMAP_PORT: int = 993
    IMAP_USERNAME: str = ""
    IMAP_PASSWORD: str = ""
    IMAP_FOLDER: str = "Design Revisions"
    IMAP_POLL_INTERVAL: int = 60
    
    # File Storage
    PROJECTS_ROOT: Path = Path.home() / "Projects"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    DEFAULT_PIN: str = "0000"  # User should change this
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
