import uuid
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from config import settings

_s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
)


def ensure_bucket_exists() -> None:
    try:
        _s3_client.head_bucket(Bucket=settings.s3_bucket_name)
    except ClientError:
        _s3_client.create_bucket(Bucket=settings.s3_bucket_name)


def upload_file(file: UploadFile, folder: str) -> str:
    extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    object_key = f"{folder}/{uuid.uuid4()}.{extension}"

    file.file.seek(0)
    _s3_client.upload_fileobj(
        file.file,
        settings.s3_bucket_name,
        object_key,
        ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
    )
    return object_key


def upload_bytes(data: bytes, folder: str, extension: str, content_type: str) -> str:
    object_key = f"{folder}/{uuid.uuid4()}.{extension}"
    _s3_client.upload_fileobj(
        BytesIO(data),
        settings.s3_bucket_name,
        object_key,
        ExtraArgs={"ContentType": content_type},
    )
    return object_key


def get_presigned_url(object_key: str, expires_in: int = 3600) -> str:
    return _s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": object_key},
        ExpiresIn=expires_in,
    )


def delete_file(object_key: str) -> None:
    _s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=object_key)