from pydantic import BaseModel

from core.fastapi.schemas.hashid import HashId


class SwipeSchema(BaseModel):
    id: int
    like: bool
    user_id: HashId
    recipe_id: int

    class Config:
        orm_mode = True