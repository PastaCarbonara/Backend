from core.exceptions.base import CustomException


class DateTooOldException(CustomException):
    code = 400
    error_code = "SWIPE_SESSION__BAD_DATE"
    message = "swipe session date should be today or newer"
