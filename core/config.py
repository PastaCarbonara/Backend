import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    WRITER_DB_URL: str = (
        f"postgresql+asyncpg://postgres:postgres@localhost:3301/mealmatch"
    )
    READER_DB_URL: str = (
        f"postgresql+asyncpg://postgres:postgres@localhost:3301/mealmatch"
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    SENTRY_SDN: str = None
    CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    AZURE_BLOB_ACCOUNT_URL: str = os.getenv("AZURE_BLOB_ACCOUNT_URL")
    IMAGE_CONTAINER_NAME: str = os.getenv("IMAGE_CONTAINER_NAME")
    AZURE_BLOB_CONNECTION_STRING: str = os.getenv("AZURE_BLOB_CONNECTION_STRING")


class DevelopmentConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DU')}:{os.getenv('DP')}@{os.getenv('H')}:{os.getenv('P')}/{os.getenv('DB')}"
    READER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DU')}:{os.getenv('DP')}@{os.getenv('H')}:{os.getenv('P')}/{os.getenv('DB')}"
    AZURE_BLOB_ACCOUNT_URL: str = os.getenv("AZURE_BLOB_ACCOUNT_URL")
    IMAGE_CONTAINER_NAME: str = os.getenv("IMAGE_CONTAINER_NAME")
    AZURE_BLOB_CONNECTION_STRING: str = os.getenv("AZURE_BLOB_CONNECTION_STRING")

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class LocalConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DU')}:{os.getenv('DP')}@{os.getenv('H')}:{os.getenv('P')}/{os.getenv('DB')}"
    READER_DB_URL: str = f"postgresql+asyncpg://{os.getenv('DU')}:{os.getenv('DP')}@{os.getenv('H')}:{os.getenv('P')}/{os.getenv('DB')}"
    AZURE_BLOB_ACCOUNT_URL: str = os.getenv("AZURE_BLOB_ACCOUNT_URL")
    IMAGE_CONTAINER_NAME: str = os.getenv("IMAGE_CONTAINER_NAME")
    AZURE_BLOB_CONNECTION_STRING: str = os.getenv("AZURE_BLOB_CONNECTION_STRING")


class ProductionConfig(Config):
    DEBUG: str = False
    WRITER_DB_URL: str = f"postgresql+asyncpg://fastapi:fastapi@localhost:3303/prod"
    READER_DB_URL: str = f"postgresql+asyncpg://fastapi:fastapi@localhost:3303/prod"


class TestConfig(Config):
    WRITER_DB_URL: str = f"sqlite+aiosqlite:///./test.db"
    READER_DB_URL: str = f"sqlite+aiosqlite:///./test.db"


def get_config():
    env = os.getenv("ENV", "local")
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
        "test": TestConfig(),
    }
    return config_type[env]


config: Config = get_config()
