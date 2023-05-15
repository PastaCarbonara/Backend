from core.exceptions import CustomException


class FilterNotExists(CustomException):
    code = 400
    error_code = "FILTER__NOT_EXISTS"
    message = "Filter does not exist"
