from core.exceptions import CustomException


class InvalidImageException(CustomException):
    code = 400
    error_code = "INVALID_IMAGE"
    message = "Image is invalid"


class AzureImageUploadException(CustomException):
    code = 400
    error_code = "AZURE_UPLOAD_FAILURE"
    message = "something went wrong with uploading the image to Azure"
