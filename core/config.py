from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Portfolio Backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./portfolio.db"
    
    # SMTP Settings for Gmail
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "mishra123best@gmail.com"
    SMTP_PASSWORD: str = ""  # You will need to put your Google App Password here
    EMAIL_TO: str = "mishra123best@gmail.com"
    FORMSPREE_URL: str = "https://formspree.io/f/movlwrzv" # Default Formspree URL
    
    class Config:
        env_file = ".env"

    @property
    def BRAIN_DIR(self) -> str:
        import os
        from pathlib import Path
        # Fallback to the hardcoded one if env is not set, but try to be smart
        default_path = r"C:\Users\user\.gemini\antigravity\brain\3e04d644-759d-4358-9068-db1f5cc39b41"
        return os.environ.get("BRAIN_DIR", default_path)

settings = Settings()
