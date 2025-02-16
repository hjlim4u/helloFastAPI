import os
from pathlib import Path
from pydantic import field_validator, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from sqlalchemy.engine.url import URL
from dotenv import load_dotenv

# 현재 파일의 디렉토리 경로를 기준으로 .env 파일 경로 설정
env_path = Path(__file__).parent.parent / '.env'

print(f"\nBefore loading .env:")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")

# .env 파일 명시적 로드 (override=True로 설정)
load_dotenv(env_path, override=True)

print(f"\nAfter loading .env:")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")

class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Session
    SESSION_EXPIRE_MINUTES: int
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            # "?client_encoding=utf8"
        )

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

    # PostgreSQL 컨테이너의 기본 환경변수 무시
    @field_validator('POSTGRES_PORT', mode='before')
    def validate_postgres_port(cls, v: int) -> int:
        return int(os.getenv('POSTGRES_PORT', '25000'))  # .env 파일의 값 우선 사용

    @field_validator('POSTGRES_PASSWORD')
    def validate_postgres_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('PostgreSQL password must be at least 8 characters long')
        return v

    # Redis 관련 검증
    @field_validator('REDIS_PORT')
    def validate_redis_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError('Redis port must be between 1 and 65535')
        return v

    @field_validator('REDIS_DB')
    def validate_redis_db(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Redis DB index must be non-negative')
        return v

    # JWT 관련 검증
    @field_validator('SECRET_KEY')
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters long')
        return v

    @field_validator('ALGORITHM')
    def validate_algorithm(cls, v: str) -> str:
        allowed_algorithms = ['HS256', 'HS384', 'HS512']
        if v not in allowed_algorithms:
            raise ValueError(f'JWT algorithm must be one of {allowed_algorithms}')
        return v

    @field_validator('ACCESS_TOKEN_EXPIRE_MINUTES')
    def validate_token_expire(cls, v: int) -> int:
        if not 5 <= v <= 1440:  # 5분에서 24시간 사이
            raise ValueError('Token expiration must be between 5 and 1440 minutes')
        return v

    @field_validator('SESSION_EXPIRE_MINUTES')
    def validate_session_expire(cls, v: int) -> int:
        if not 5 <= v <= 1440:  # 5분에서 24시간 사이
            raise ValueError('Session expiration must be between 5 and 1440 minutes')
        return v

print(f"\n.env file path: {env_path}")
print(f"File exists: {env_path.exists()}")

print("\nEnvironment variables from .env file:")
print("Database settings:")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")

print("\nRedis settings:")
print(f"REDIS_HOST: {os.getenv('REDIS_HOST')}")
print(f"REDIS_PORT: {os.getenv('REDIS_PORT')}")
print(f"REDIS_DB: {os.getenv('REDIS_DB')}")

# settings 인스턴스 생성
settings = Settings()

print("\nLoaded Settings instance:")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Database Host: {settings.POSTGRES_HOST}")
print(f"Database Port: {settings.POSTGRES_PORT}")
print(f"Redis Host: {settings.REDIS_HOST}")
print(f"Redis Port: {settings.REDIS_PORT}")

print("\nEnvironment variables:")
print(f"Container POSTGRES_PORT: {os.environ.get('POSTGRES_PORT')}")  # PostgreSQL 컨테이너의 값
print(f"ENV file POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")       # .env 파일의 값

print("\nLoaded Settings:")
print(f"Final POSTGRES_PORT: {settings.POSTGRES_PORT}")              # 최종 사용되는 값

print("\nAfter Settings initialization:")
print(f"Settings POSTGRES_PORT: {settings.POSTGRES_PORT}")
print(f"Environment POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")

print("\nFinal settings:")
print(f"Settings POSTGRES_PORT: {settings.POSTGRES_PORT}")
print(f"Environment POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}") 