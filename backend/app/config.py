from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    # Ejemplo para SQL Server (ajusta usuario, password, host, puerto, base y driver)
    # mssql+pyodbc://usuario:password@host:puerto/base?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
    DATABASE_URL: str = "mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/docu_dash?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    
    # Server
    PORT: int = 3001
    ENVIRONMENT: str = "development"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN_DAYS: int = 7
    
    # CORS
    CORS_ORIGIN: str = "http://localhost:5173"
    
    # Azure DevOps Integration (optional)
    AZURE_DEVOPS_ORG_URL: Optional[str] = None
    AZURE_DEVOPS_PAT: Optional[str] = None
    AZURE_DEVOPS_PROJECT: Optional[str] = None
    
    # GitLab Integration (optional)
    GITLAB_URL: Optional[str] = None
    GITLAB_TOKEN: Optional[str] = None
    
    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_FROM: str = "DashCase <noreply@dashcase.com>"
    
    # Frontend URL (for notifications)
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

