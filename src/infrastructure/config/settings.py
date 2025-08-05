from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # Database
    database_url: str
    test_database_url: str
    
    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # Email
    email_from: str
    email_enabled: bool


# Global settings instance
settings = Settings()