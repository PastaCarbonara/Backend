from core.exceptions.base import CustomException


class BadEncryptedStringException(CustomException):
    code = 400
    error_code = "AUTH__BAD_ENCRYPTION"
    message = "submitted string is encrypted incorrectly"


class BadEncryptedUUIDException(CustomException):
    code = 400
    error_code = "AUTH__BAD_UUID"
    message = "submitted string is not a uuid"
