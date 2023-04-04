from enum import Enum, auto


class BaseEnum(Enum):
    pass


class UserEnum(BaseEnum):
    pass


class SwipeSessionActionEnum(str, BaseEnum):
    # When editing this, edit app\swipe_session\services\action_docs.py too
    CONNECTION_CODE = "CONNECTION_CODE"
    SESSION_MESSAGE = "SESSION_MESSAGE"
    GLOBAL_MESSAGE = "GLOBAL_MESSAGE"
    RECIPE_SWIPE = "RECIPE_SWIPE"
    RECIPE_MATCH = "RECIPE_MATCH"


class SwipeSessionEnum(str, BaseEnum):
    PAUSED = "Gepauzeerd"
    CANCELLED = "Gestopt"
    IN_PROGRESS = "Is bezig"
    COMPLETED = "Voltooid"
