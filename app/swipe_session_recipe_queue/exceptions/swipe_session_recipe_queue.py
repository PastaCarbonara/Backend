from core.exceptions import CustomException


class QueueAlreadyExistsException(CustomException):
    code = 409
    error_code = "SWIPE_SESSION_RECIPE_QUEUE__ALREADY_EXISTS"
    message = "queue already exists for this swipe session"


class QueueItemAlreadyExistsException(CustomException):
    code = 409
    error_code = "SWIPE_SESSION_RECIPE_QUEUE__ITEM_ALREADY_EXISTS"
    message = "queue already has an item with given recipe"
