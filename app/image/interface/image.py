"""Interface for image storage."""

from abc import ABC, abstractmethod
from fastapi import UploadFile

from azure.storage.blob.aio import BlobServiceClient
from core.config import config


class ObjectStorageInterface(ABC):
    @classmethod
    @abstractmethod
    async def upload_image(cls, image: UploadFile, unique_filename: str) -> None:
        pass

    @classmethod
    @abstractmethod
    async def delete_image(cls, filename: str) -> None:
        pass


class AzureBlobInterface(ObjectStorageInterface):
    account_url = config.AZURE_BLOB_ACCOUNT_URL
    container_name = config.IMAGE_CONTAINER_NAME
    connection_string = config.AZURE_BLOB_CONNECTION_STRING

    @classmethod
    async def upload_image(cls, image: UploadFile, unique_filename: None):
        blob_service_client = BlobServiceClient.from_connection_string(
            cls.connection_string
        )
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(
                cls.container_name
            )
            blob_client = container_client.get_blob_client(unique_filename)
            f = image.file.read()
            await blob_client.upload_blob(f)

    @classmethod
    async def delete_image(cls, filename: str) -> None:
        blob_service_client = BlobServiceClient.from_connection_string(
            cls.connection_string
        )

        async with blob_service_client:
            blob_client = blob_service_client.get_blob_client(
                container=cls.container_name, blob=filename
            )
            await blob_client.delete_blob()


class GCoreInterface(ObjectStorageInterface):
    @classmethod
    async def upload_image(cls, image: UploadFile, unique_filename: str) -> None:
        ...

    @classmethod
    async def delete_image(cls, filename: str) -> None:
        ...


class GoogleBucketInterface(ObjectStorageInterface):
    @classmethod
    async def upload_image(cls, image: UploadFile, unique_filename: str) -> None:
        ...

    @classmethod
    async def delete_image(cls, filename: str) -> None:
        ...
