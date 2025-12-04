from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Rota-v1 Financial Platform"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    
    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "rota"
    POSTGRES_PASSWORD: str = "securepassword"
    POSTGRES_DB: str = "rota_db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    # External APIs
    FINNHUB_API_KEY: str = "d4ocg0pr01quuso8ub7gd4ocg0pr01quuso8ub80"
    ALPHA_VANTAGE_API_KEY: str = "OSB2R03Z0KQPMM9A"
    PERIGON_API_KEY: str = "cebd04f3-bfcb-477a-b9c3-9c2d2c03030c"
    MASSIVE_API_KEY: str = "q0ngVF2HTCUKx7MzPWPyFUvXqZdsWGUy"
    PRIXE_API_KEY: str = "test_7c474e9515009f2db10d94400a6658e3c59dda218fe28f32da7f3b32aeff4219"




    # Security
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    def model_post_init(self, __context):
        if self.SQLALCHEMY_DATABASE_URI is None:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        
        if self.REDIS_URL is None:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        case_sensitive = True

settings = Settings()
