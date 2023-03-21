from pydantic import BaseModel


class SwipeSchema(BaseModel):
    id: int
    like: bool
    user_id: int
    recipe_id: int