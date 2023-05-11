from core.exceptions import CustomException


class CorruptImageException(CustomException):
    code = 400
    error_code = "CORRUPT_IMAGE"
    message = "Image is corrupt"


class InvalidFileTypeException(CustomException):
    code = 400
    error_code = "INVALID_IMAGE"
    message = "Image is invalid"


class InvalidImageException(CustomException):
    code = 400
    error_code = "UNSUPPORTED_IMAGE"
    message = "WE ONLY SUPPORT JPG, PNG"


class ImageTooLargeException(CustomException):
    code = 400
    error_code = "IMAGE_TOO_LARGE"
    message = "Image is too big, maximum = 5MB"


class AzureImageUploadException(CustomException):
    code = 400
    error_code = "AZURE_UPLOAD_FAILURE"
    message = "something went wrong with uploading the image to Azure"


class AzureImageDeleteException(CustomException):
    code = 400
    error_code = "AZURE_DELETE_FAILURE"
    message = "something went wrong with deleting the image from Azure"


class AzureImageDeleteNotFoundException(AzureImageDeleteException):
    message = "Azure image not found"


class FileDependecyException(CustomException):
    code = 409
    error_code = "FILE__IS_IN_USE"
    message = "The image is being used."


class DuplicateFileNameException(CustomException):
    code = 400
    error_code = "FILE__DUPLICATE_FILENAME"
    message = "Filename already in use"


class FileNotFoundException(CustomException):
    code = 400
    error_code = "FILE__NOT_FOUND"
    message = "File not found"
