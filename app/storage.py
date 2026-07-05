import uuid
import boto3
from fastapi import UploadFile

from app.config import settings

if settings.aws_access_key_id and settings.aws_secret_access_key:
    # Local dev: explicit keys from .env
    s3_client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
else:
    # EC2: no keys provided, boto3 uses the attached IAM Role automatically
    s3_client = boto3.client("s3", region_name=settings.aws_region)


def save_file_locally(file: UploadFile) -> str:
    """Uploads the file to S3 and returns the S3 object key (used as 'filename')."""
    extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}.{extension}" if extension else uuid.uuid4().hex

    s3_client.upload_fileobj(
        file.file,
        settings.s3_bucket_name,
        unique_filename,
        ExtraArgs={"ContentType": file.content_type},
    )
    return unique_filename


def delete_file_locally(filename: str) -> None:
    s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=filename)