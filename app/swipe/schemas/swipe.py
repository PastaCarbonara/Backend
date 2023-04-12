from pydantic import BaseModel
from core.fastapi.schemas.hashid import DehashId, HashId


class SwipeSchema(BaseModel):
    id: int
    like: bool
    swipe_session_id: HashId
    recipe_id: int
    user_id: HashId

    class Config:
        orm_mode = True


class CreateSwipeSchema(BaseModel):
    user_id: DehashId
    like: bool
    swipe_session_id: DehashId
    recipe_id: int
