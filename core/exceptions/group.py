from core.exceptions import CustomException


class GroupNotFoundException(CustomException):
    code = 404
    error_code = "GROUP__NOT_FOUND"
    message = "group not found"


class GroupJoinConflictException(CustomException):
    code = 409
    error_code = "GROUP__JOIN_CONFLICT"
    message = "user has already joined this group"
