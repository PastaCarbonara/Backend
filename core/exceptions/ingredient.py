from core.exceptions import CustomException


class IngredientAlreadyExistsException(CustomException):
    code = 409
    error_code = "INGREDIENT__ALREADY_EXISTS"
    message = "the submitted ingredient name is already taken"
