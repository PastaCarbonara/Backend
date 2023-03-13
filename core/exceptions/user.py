from core.exceptions import CustomException


class PasswordDoesNotMatchException(CustomException):
    code = 401
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "password does not match"


class IncorrectPasswordException(CustomException):
    code = 403
    error_code = "USER__INCORRECT_PASSWORD"
    message = "password is incorrect"


class DuplicateUsernameException(CustomException):
    code = 400
    error_code = "USER__DUPLICATE_USERNAME"
    message = "duplicate username"


class UserNotFoundException(CustomException):
    code = 404
    error_code = "USER__NOT_FOUND"
    message = "user not found"


class MissingUserIDException(CustomException):
    code = 400
    error_code = "USER__NO_ID"
    message = "no id was provided, or was not logged in"
