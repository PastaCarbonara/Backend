from core.exceptions import CustomException


class GroupNotFoundException(CustomException):
    code = 404
    error_code = "GROUP__NOT_FOUND"
    message = "group not found"
