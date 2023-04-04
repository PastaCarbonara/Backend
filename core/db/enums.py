from enum import Enum, auto


class BaseEnum(Enum):
    pass


class UserEnum(BaseEnum):
    pass


class SwipeSessionActionEnum(str, BaseEnum):
    # When editing this, edit app\swipe_session\services\action_docs.py too
    CONNECTION_CODE = "CONNECTION_CODE"
    GLOBAL_MESSAGE = "GLOBAL_MESSAGE"
    RECIPE_MATCH = "RECIPE_MATCH"
    RECIPE_SWIPE = "RECIPE_SWIPE"
    SESSION_MESSAGE = "SESSION_MESSAGE"
    SESSION_STATUS_UPDATE = "SESSION_STATUS_UPDATE"


class SwipeSessionEnum(str, BaseEnum):
    CANCELLED = "Gestopt"
    COMPLETED = "Voltooid"
    IN_PROGRESS = "Is bezig"
    PAUSED = "Gepauzeerd"
    READY = "Staat klaar"
