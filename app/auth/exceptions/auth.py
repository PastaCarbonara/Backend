from core.exceptions.base import CustomException


class BadUUIDException(CustomException):
    code = 400
    error_code = "AUTH__BAD_UUID"
    message = "submitted value is not a uuid"
