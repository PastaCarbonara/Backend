from pydantic import BaseModel, Field


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
