from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    API_KEY: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:8000"]

    FACE_DETECTION_MODEL: str = "hog"
    FACE_ENCODING_MODEL: str = "large"
    TOLERANCE: float = 0.6
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    class Config:
        env_file = ".env"


settings = Settings()
