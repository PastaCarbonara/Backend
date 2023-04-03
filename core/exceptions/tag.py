from core.exceptions import CustomException


class TagAlreadyExistsException(CustomException):
    code = 409
    error_code = "TAG__ALREADY_EXISTS"
    message = "the submitted tag name is already taken"
