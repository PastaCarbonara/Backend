from core.exceptions import CustomException


class AzureImageUploadException(CustomException):
    code = 400
    error_code = "AZURE_UPLOAD_FAILURE"
    message = "something went wrong with uploading the image to Azure"
