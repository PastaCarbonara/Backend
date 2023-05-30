from core.exceptions.base import CustomException


class DateTooOldException(CustomException):
    code = 400
    error_code = "SWIPE_SESSION__BAD_DATE"
    message = "swipe session date should be today or newer"


class SwipeSessionNotFoundException(CustomException):
    code = 404
    error_code = "SWIPE_SESSION__NOT_FOUND"
    message = "swipe session was not found"
