from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    supabase_url: str
    supabase_key: str
    jwt_secret: str = Field(min_length=32)
    app_origin: str = 'http://127.0.0.1:8000'
    cookie_secure: bool = False

    @field_validator('supabase_url')
    @classmethod
    def validate_supabase(cls, value: str) -> str:
        url = urlsplit(value)
        if url.scheme != 'https' or not url.netloc or url.path not in ('', '/'):
            raise ValueError('SUPABASE_URL은 https 프로젝트 기본 주소여야 합니다.')
        return value.rstrip('/')

    @field_validator('app_origin')
    @classmethod
    def validate_origin(cls, value: str) -> str:
        url = urlsplit(value)
        if url.scheme not in ('http', 'https') or not url.netloc or url.path not in ('', '/'):
            raise ValueError('APP_ORIGIN은 경로 없는 사이트 주소여야 합니다.')
        return value.rstrip('/')


@lru_cache
def get_settings() -> Settings:
    return Settings()
