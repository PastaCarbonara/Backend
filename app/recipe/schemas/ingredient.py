from pydantic import BaseModel, Field


class IngredientSchema(BaseModel):
    id: int = Field(..., description="Ingredient ID")

    class Config:
        orm_mode = True


class GetIngredientSchema(BaseModel):
    id: int = Field(..., description="Ingredient ID")
    name: str = Field(..., description="Ingrdient name")

    class Config:
        orm_mode = True
