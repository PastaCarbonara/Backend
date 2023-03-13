from core.exceptions import CustomException

class RecipeNotFoundExeption(CustomException):
    code = 404
    error_code = "RECIPE__RECIPE_NOT_FOUND"
    message = "recipe was not found in the database"
