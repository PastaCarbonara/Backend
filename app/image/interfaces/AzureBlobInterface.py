from typing import List
from fastapi import UploadFile

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient, BlobClient
from core.config import config
from image.utils import generate_unique_filename
from image.exceptions.image import AzureImageUploadException

# try:
#     print("Azure Blob Storage Python quickstart sample")

#     # Quickstart code goes here

# except Exception as ex:
#     print("Exception:")
#     print(ex)

# # Create a local directory to hold blob data
# local_path = "./data"
# os.mkdir(local_path)

# # Create a file in the local data directory to upload and download
# local_file_name = str(uuid.uuid4()) + ".txt"
# upload_file_path = os.path.join(local_path, local_file_name)

# # Write text to the file
# file = open(file=upload_file_path, mode="w")
# file.write("Hello, World!")
# file.close()


account_url = "https://munchiestore.blob.core.windows.net"
container_name = "munchie-images"
default_credential = DefaultAzureCredential()
connection_string = "DefaultEndpointsProtocol=https;AccountName=munchiestore;AccountKey=qGiBfulFQCq4Fb6llMXeF7sp/8ec35mX6ri7EoYLBlAmkYTk0ShaQp1K909quwfOVHWkJ0gFcRLe+AStJ+vkhQ==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
# Create a blob client using the local file name as the name for the blob
# blob_client = blob_service_client.get_blob_client(
#     container=container_name, blob=local_file_name
# )

# print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)


# async def upload():  # Upload the created file
#     async with BlobClient.from_connection_string(
#         connection_string, container_name=container_name, blob_name=local_file_name
#     ) as blob:

#         with open(file=upload_file_path, mode="rb") as data:
#             await blob.upload_blob(data)


print(blob_service_client.get_container_client(container_name).url)


class AzureBlobInterface:
    account_url = config.AZURE_BLOB_ACCOUNT_URL
    container_name = config.IMAGE_CONTAINER_NAME
    connection_string = config.AZURE_BLOB_CONNECTION_STRING
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    @classmethod
    async def upload_image(image: UploadFile) -> str:

        unique_filename = generate_unique_filename(image.filename)

        async with blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            try:
                blob_client = container_client.get_blob_client(unique_filename)
                f = await image.read()
                await blob_client.upload_blob(f)
            except Exception as e:
                return AzureImageUploadException
        return unique_filename
