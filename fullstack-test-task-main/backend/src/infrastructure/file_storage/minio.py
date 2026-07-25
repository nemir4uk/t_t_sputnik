from minio import Minio
from src.infrastructure.config import settings


minio_client = Minio(
    endpoint=settings.s3_endpoint,
    access_key=settings.s3_access_key,
    secret_key=settings.s3_secret_key,
    secure=False,
)


def init_bucket():
    bucket = settings.s3_bucket
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)
