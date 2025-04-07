# app/core/config.py

import os
import secrets
from typing import ClassVar
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastPleasure"
    PROJECT_VERSION: str = "2.0.0"
    SECRET_KEY: ClassVar[str] = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        from_attributes = True

settings = Settings()

# app/core/config.py
import os
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseSettings

def get_secret():
    secret_name = os.getenv("DB_SECRET_NAME")
    region_name = os.getenv("AWS_REGION", "us-east-2")

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        secret = get_secret_value_response['SecretString']
        return eval(secret)  # Convierte el string JSON a dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastPleasure"
    PROJECT_VERSION: str = "3.0"
    SECRET_KEY: ClassVar[str] = os.getenv("SECRET_KEY", secrets.token_hex(32))
    # Estos valores serán sobrescritos por Secrets Manager si está configurado
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "mydatabase"
    DB_PORT: str = "5432"
    
    class Config:
        case_sensitive = True

settings = Settings()

# Intenta obtener secretos de AWS Secrets Manager
try:
    secret = get_secret()
    settings.DB_HOST = secret.get('host', settings.DB_HOST)
    settings.DB_USER = secret.get('username', settings.DB_USER)
    settings.DB_PASSWORD = secret.get('password', settings.DB_PASSWORD)
    settings.DB_NAME = secret.get('dbname', settings.DB_NAME)
    settings.DB_PORT = secret.get('port', settings.DB_PORT)
except:
    # Usa valores por defecto si no puede acceder a Secrets Manager
    pass