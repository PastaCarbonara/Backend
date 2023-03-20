from pydantic import BaseModel


class CreateSwipeSchema(BaseModel):
    like: bool
    user_id: int
    recipe_id: int


class SwipeSchema(BaseModel):
    id: int
    like: bool
    user_id: int
    recipe_id: int