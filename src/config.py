import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


MAX_POST_SIZE = 1_048_576

# Base
DATABASE_URL = os.environ.get("DATABASE_URL")

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
API_SHARED_TOKEN = os.environ.get("API_SHARED_TOKEN")
EXTERNAL_TOKEN = os.environ.get("EXTERNAL_TOKEN")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

ENVIRONMENT = os.environ.get("ENVIRONMENT")

REDIS_SSL_CERT = (
    os.environ.get("REDIS_SSL_CERT") if ENVIRONMENT == "production" else None
)

REDIS_USE_TLS = None


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )


class JwtOAuthConfig(EnvSettings):
    secret_key: str | None = os.environ.get("SECRET_KEY")
    algorithm: str = 'HS256'
    access_token_expire_minutes = 30



class DBParams(EnvSettings):
    url: str = Field(..., alias='DATABASE_URL')


class RedisParams(EnvSettings):
    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(..., alias='REDIS_PORT')
    password: str = Field(..., alias='REDIS_PASSWORD')
    ssl_cert: str = Field(..., alias='REDIS_SSL_CERT')
    use_ttl: str = Field(..., alias='REDIS_USE_TLS')


class GeneralParams(EnvSettings):
    environment: str = Field(..., alias='ENVIRONMENT')


class Config(EnvSettings):
    db: DBParams = DBParams()
    redis: RedisParams = RedisParams()
    general: GeneralParams = GeneralParams()
    jwt: JwtOAuthConfig = JwtOAuthConfig()


@lru_cache
def get_config() -> Config:
    return Config()
