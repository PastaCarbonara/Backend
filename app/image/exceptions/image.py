from core.exceptions import CustomException


class FileIsNotImageException(CustomException):
    code = 400
    error_code = "FILE_NOT_IMAGE"
    message = "File is not an image"


class InvalidFileTypeException(CustomException):
    code = 400
    error_code = "INVALID_IMAGE"
    message = "Image is invalid"


class InvalidImageException(CustomException):
    code = 400
    error_code = "INVALID_IMAGE"
    message = "Image is invalid"


class ImageTooLargeException(CustomException):
    code = 400
    error_code = "IMAGE_TOO_LARGE"
    message = "Image is too big, maximum = 10MB"


class AzureImageUploadException(CustomException):
    code = 400
    error_code = "AZURE_UPLOAD_FAILURE"
    message = "something went wrong with uploading the image to Azure"


class DuplicateFileNameException(CustomException):
    code = 400
    error_code = "DUPLICATE_FILENAME"
    message = "THIS_FILE_ALREADY_EXISTS"


class FileNotFoundException(CustomException):
    code = 400
    error_code = "FILE_NOT_FOUND"
    message = "THIS_FILE_NOT_FOUND"
