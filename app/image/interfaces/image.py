from abc import ABC, abstractmethod
from fastapi import UploadFile

from azure.storage.blob.aio import BlobServiceClient
from core.config import config
from app.image.exceptions.image import AzureImageUploadException


class ObjectStorageInterface(ABC):
    @staticmethod
    @abstractmethod
    async def upload_image(self, image: UploadFile, unique_filename: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    async def delete_image(self, filename: str) -> None:
        pass


class AzureBlobInterface(ObjectStorageInterface):
    account_url = config.AZURE_BLOB_ACCOUNT_URL
    container_name = config.IMAGE_CONTAINER_NAME
    connection_string = config.AZURE_BLOB_CONNECTION_STRING
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    @staticmethod
    async def upload_image(cls, image: UploadFile, unique_filename: str) -> str:
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

    @staticmethod
    async def delete_image(cls, filename: str) -> None:
        ...


class GCoreInterface(ObjectStorageInterface):
    @staticmethod
    async def upload_image(cls, image: UploadFile, unique_filename: str) -> str:
        ...

    @staticmethod
    async def delete_image(cls, filename: str) -> None:
        ...


class GoogleBucketInterface(ObjectStorageInterface):
    @staticmethod
    async def upload_image(cls, image: UploadFile, unique_filename: str) -> str:
        ...

    @staticmethod
    async def delete_image(cls, filename: str) -> None:
        ...
