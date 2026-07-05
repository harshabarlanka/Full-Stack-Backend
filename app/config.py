from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_bucket_name: str

    class Config:
        env_file = ".env"

settings = Settings()