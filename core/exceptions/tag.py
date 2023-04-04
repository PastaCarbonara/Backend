from core.exceptions import CustomException


class TagAlreadyExistsException(CustomException):
    code = 409
    error_code = "TAG__ALREADY_EXISTS"
    message = "the submitted tag name is already taken"


class TagNotFoundException(CustomException):
    code = 404
    error_code = "TAG_NOT_FOUND"
    message = "tag was not found in the database"
