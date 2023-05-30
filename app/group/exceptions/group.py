from core.exceptions.base import CustomException


class GroupNotFoundException(CustomException):
    code = 404
    error_code = "GROUP__NOT_FOUND"
    message = "group not found"


class GroupJoinConflictException(CustomException):
    code = 409
    error_code = "GROUP__JOIN_CONFLICT"
    message = "user has already joined this group"


class NotInGroupException(CustomException):
    code = 400
    error_code = "GROUP__NOT_JOINED"
    message = "user is not in this group"


class AdminLeavingException(CustomException):
    code = 400
    error_code = "GROUP__ADMIN_LEAVE"
    message = "group admin cannot leave the group"
