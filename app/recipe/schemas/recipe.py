from pydantic import BaseModel, Field


class GetRecipeListResponseSchema(BaseModel):
    recipe_id: int = Field(..., description="ID")

    class Config:
        orm_mode = True


class JudgeRecipeRequestSchema(BaseModel):
    user_id: int = Field(..., description="userID")
    like: bool = Field(..., description="Of je de recept leuk vindt")

    class Config:
        orm_mode = True
