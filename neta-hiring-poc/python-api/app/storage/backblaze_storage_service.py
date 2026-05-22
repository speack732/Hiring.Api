from typing import BinaryIO

import boto3
from botocore.client import Config
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.config import Settings, get_settings


class BackblazeStorageService:
    def __init__(self, settings: Settings) -> None:
        missing_settings = [
            name
            for name, value in {
                "BACKBLAZE_ENDPOINT": settings.backblaze_endpoint,
                "BACKBLAZE_BUCKET": settings.backblaze_bucket,
                "BACKBLAZE_ACCESS_KEY": settings.backblaze_access_key,
                "BACKBLAZE_SECRET_KEY": settings.backblaze_secret_key,
            }.items()
            if not value
        ]
        if missing_settings:
            raise ValueError(
                "Missing Backblaze configuration: " + ", ".join(missing_settings)
            )

        self.bucket = settings.backblaze_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.backblaze_endpoint,
            aws_access_key_id=settings.backblaze_access_key,
            aws_secret_access_key=settings.backblaze_secret_key,
            config=Config(s3={"addressing_style": "path"}),
        )

    async def upload_async(self, file: UploadFile, key: str) -> str:
        await file.seek(0)
        await run_in_threadpool(self._put_object, file.file, key, file.content_type)
        return key

    async def delete_async(self, key: str) -> None:
        await run_in_threadpool(
            self._client.delete_object,
            Bucket=self.bucket,
            Key=key,
        )

    def _put_object(
        self,
        stream: BinaryIO,
        key: str,
        content_type: str | None,
    ) -> None:
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=stream,
            ContentType=content_type or "application/octet-stream",
        )


def get_storage_service() -> BackblazeStorageService:
    return BackblazeStorageService(get_settings())
