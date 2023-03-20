from enum import Enum


class BaseEnum(Enum):
    pass


class UserEnum(BaseEnum):
    pass


class SwipeSessionEnum(str, BaseEnum):
    PAUSED = "Gepauzeerd"
    CANCELLED = "Gestopt"
    IN_PROGRESS = "Is bezig"
    COMPLETED = "Voltooid"
