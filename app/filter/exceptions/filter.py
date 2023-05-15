from core.exceptions import CustomException


class FilterNotExists(CustomException):
    code = 400
    error_code = "FILTER__NOT__EXISTS"
    message = "Filter does not exist"
