from pydantic import BaseModel


class CreateSwipeSchema(BaseModel):
    like: bool
    swipe_session_id: int | str
    recipe_id: int
    user_id: int | None = None
