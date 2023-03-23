from pydantic import BaseModel, Field


class CreateIngredientSchema(BaseModel):
    name: str


class IngredientSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class RecipeIngredientSchema(BaseModel):
    ingredient_id: int = Field(..., description="ID")
    name: str = Field(..., name="Ingredient")
    amount: int = Field(..., name="Hoeveelheid")
    unit: str = Field

    class Config:
        orm_mode = True


class GetRecipeListResponseSchema(BaseModel):
    recipe_id: int = Field(..., description="ID")

    class Config:
        orm_mode = True
