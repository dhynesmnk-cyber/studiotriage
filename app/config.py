from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Little Desk"
    DEBUG: bool = False
    
    # Database - Use absolute path for containerized deployments
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./little_desk.db")
    
    # Ollama Local LLM
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "poolside")
    
    # IMAP Configuration
    IMAP_SERVER: str = os.getenv("IMAP_SERVER", "")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))
    IMAP_USERNAME: str = os.getenv("IMAP_USERNAME", "")
    IMAP_PASSWORD: str = os.getenv("IMAP_PASSWORD", "")
    IMAP_FOLDER: str = os.getenv("IMAP_FOLDER", "Design Revisions")
    IMAP_POLL_INTERVAL: int = int(os.getenv("IMAP_POLL_INTERVAL", "60"))
    
    # File Storage - Use /data for containerized deployments (Render/Railway)
    PROJECTS_ROOT: Path = Path(os.getenv("PROJECTS_ROOT", Path.home() / "Projects"))
    
    # Security - Must be set in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    DEFAULT_PIN: str = os.getenv("DEFAULT_PIN", "0000")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
