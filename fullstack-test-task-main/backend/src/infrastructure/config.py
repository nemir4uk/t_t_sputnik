from pathlib import Path
from os import getenv
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings
load_dotenv(find_dotenv())


BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = (BASE_DIR / "storage" / "files").resolve()
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class Setting(BaseSettings):

    pg_host: str = getenv('POSTGRES_HOST')
    pg_port: str = getenv('PGPORT')
    pg_user: str = getenv('POSTGRES_USER')
    pg_pass: str = getenv('POSTGRES_PASSWORD')
    pg_db: str = getenv('POSTGRES_DB')

    log_level: str = getenv('LOG_LEVEL')
    retry_count: int = getenv('RETRY_COUNT')

    rabbit_host: str = getenv('RABBITMQ_HOST')
    rabbit_port: str = getenv('RABBITMQ_PORT')
    rabbit_user: str = getenv('RABBITMQ_USER')
    rabbit_pass: str = getenv('RABBITMQ_PASS')
    rabbit_queue: str = getenv('RABBITMQ_QUEUE')

    max_file_size: int = getenv('NEXT_PUBLIC_MAX_FILE_SIZE')
    allowed_extensions: str = getenv('NEXT_PUBLIC_ALLOWED_EXTENSIONS')

    storage_dir: Path = (Path(__file__).resolve().parent.parent.parent / "storage" / "files").resolve()

    s3_endpoint: str = getenv('S3_ENDPOINT')
    s3_bucket: str = getenv('S3_BUCKET')
    s3_access_key: str = getenv('S3_ACCESS_KEY')
    s3_secret_key: str = getenv('S3_SECRET_KEY')


settings = Setting()


class Base(DeclarativeBase):
    pass
