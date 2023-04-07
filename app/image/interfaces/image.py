import sys
from typing import List, Protocol
from fastapi import UploadFile

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient, BlobClient
from core.config import config
from app.image.utils import generate_unique_filename
from app.image.exceptions.image import AzureImageUploadException


class ObjectStorageInterface(Protocol):
    async def upload_image(self, image: UploadFile) -> str:
        ...

    async def delete_image(self, filename: str) -> None:
        ...


class AzureBlobInterface:
    account_url = config.AZURE_BLOB_ACCOUNT_URL
    container_name = config.IMAGE_CONTAINER_NAME
    connection_string = config.AZURE_BLOB_CONNECTION_STRING
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    @classmethod
    async def upload_image(cls, image: UploadFile) -> str:
        unique_filename = generate_unique_filename(image.filename)

        async with cls.blob_service_client:
            container_client = cls.blob_service_client.get_container_client(
                cls.container_name
            )
            blob_client = container_client.get_blob_client(unique_filename)
            f = image.file.read()
            try:
                await blob_client.upload_blob(f)
            except Exception as e:
                print(e)
                raise AzureImageUploadException()

        return unique_filename

    @classmethod
    async def delete_image(cls, filename: str) -> None:
        ...


class GCoreInterface:
    @classmethod
    async def upload_image(cls, image: UploadFile) -> str:
        ...

    @classmethod
    async def delete_image(cls, filename: str) -> None:
        ...


class GoogleBucketInterface:
    @classmethod
    async def upload_image(cls, image: UploadFile) -> str:
        ...

    @classmethod
    async def delete_image(cls, filename: str) -> None:
        ...
