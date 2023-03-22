from pydantic import BaseModel


class SwipeSchema(BaseModel):
    id: int
    like: bool
    swipe_session_id: int | str
    recipe_id: int
    user_id: int | None = None

    class Config:
        orm_mode = True


class CreateSwipeSchema(BaseModel):
    like: bool
    swipe_session_id: int | str
    recipe_id: int
    user_id: int | None = None
