# app/core/config.py
import os
import secrets
import boto3
from botocore.exceptions import ClientError
from typing import ClassVar, Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastPleasure"
    PROJECT_VERSION: str = "3.0"
    SECRET_KEY: ClassVar[str] = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Valores por defecto (serán sobrescritos si Secrets Manager está disponible)
    POSTGRES_USER: str = "default_user"
    POSTGRES_PASSWORD: str = "default_password"
    POSTGRES_DB: str = "default_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Nueva configuración para Secrets Manager
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    DB_SECRET_NAME: str = os.getenv("DB_SECRET_NAME", "prod/rds/credentials")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_secrets_from_aws()
    
    def _load_secrets_from_aws(self) -> None:
        """Intenta cargar credenciales desde AWS Secrets Manager"""
        try:
            secret = self._get_db_secret()
            
            if secret:
                self.POSTGRES_HOST = secret.get('host', self.POSTGRES_HOST)
                self.POSTGRES_USER = secret.get('username', self.POSTGRES_USER)
                self.POSTGRES_PASSWORD = secret.get('password', self.POSTGRES_PASSWORD)
                self.POSTGRES_DB = secret.get('dbname', self.POSTGRES_DB)
                self.POSTGRES_PORT = int(secret.get('port', self.POSTGRES_PORT))
                
        except Exception as e:
            # Si falla, se mantienen los valores por defecto o de .env
            print(f"Warning: Could not load secrets from AWS: {str(e)}")
    
    def _get_db_secret(self) -> Dict[str, Any]:
        """Obtiene el secreto de AWS Secrets Manager"""
        if not all([self.DB_SECRET_NAME, self.AWS_REGION]):
            return {}
            
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.AWS_REGION
        )
        
        try:
            response = client.get_secret_value(SecretId=self.DB_SECRET_NAME)
            if 'SecretString' in response:
                import json
                return json.loads(response['SecretString'])
            return {}
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Secret {self.DB_SECRET_NAME} not found")
            elif e.response['Error']['Code'] == 'AccessDeniedException':
                print(f"Access denied to secret {self.DB_SECRET_NAME}")
            else:
                print(f"Unexpected error retrieving secret: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error parsing secret: {str(e)}")
            return {}

    class Config:
        env_file = ".env"
        from_attributes = True

settings = Settings()