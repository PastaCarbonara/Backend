from pydantic import BaseModel, Field, root_validator
from pydantic.utils import GetterDict

from app.ingredient.schemas.ingredient import IngredientSchema


class CreateRecipeIngredientSchema(BaseModel):
    id: int
    amount: float
    unit: str


class FlattenedRecipeIngredientSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Tag name")
    amount: float
    unit: str

    @root_validator(pre=True)
    def flatten_recipe_tag(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        ingredient = values.get("ingredient")
        
        if ingredient is None:
            return values
        
        ingredient = IngredientSchema.validate(ingredient)
        return {
            "id": ingredient.id,
            "name": ingredient.name,
            "amount": values["amount"],
            "unit": values["unit"],
        } | dict(values)

    class Config:
        orm_mode = True



class GetIngredientSchema(BaseModel):
    id: int = Field(..., description="Ingredient ID")
    name: str = Field(..., description="Ingrdient name")

    class Config:
        orm_mode = True
