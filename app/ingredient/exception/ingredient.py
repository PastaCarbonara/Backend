"""excepions related to ingredients"""
from core.exceptions import CustomException


class IngredientAlreadyExistsException(CustomException):
    code = 409
    error_code = "INGREDIENT__ALREADY_EXISTS"
    message = "the submitted ingredient name is already taken"


class IngredientNotFoundException(CustomException):
    code = 404
    error_code = "INGREDIENT__NOT_FOUND"
    message = "the submitted ingredient does not exist"


class IngredientDependecyException(CustomException):
    code = 409
    error_code = "INGREDIENT__DEPENDENCY"
    message = "the submitted ingredient is used in a recipe"
