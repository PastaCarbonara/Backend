"""Ingredient schemas."""

from pydantic import BaseModel, Field


class CreateIngredientSchema(BaseModel):
    """
    Schema for creating a new ingredient.

    Attributes
    ----------
    name : str
        The name of the ingredient.
    """

    name: str = Field(..., description="Naam")


class IngredientSchema(BaseModel):
    """
    Schema for an ingredient.

    Attributes
    ----------
    id : int
        The ID of the ingredient.
    name : str
        The name of the ingredient.
    """

    id: int = Field(..., description="ID")
    name: str = Field(..., description="Naam")

    class Config:
        orm_mode = True


class RecipeIngredientSchema(BaseModel):
    """
    Schema for an ingredient in a recipe.

    Attributes
    ----------
    ingredient_id : int
        The ID of the ingredient.
    amount : int
        The amount of the ingredient in the recipe.
    unit : str
        The unit of measurement for the ingredient.
    """

    ingredient_id: int = Field(..., description="ID")
    amount: int = Field(..., name="Hoeveelheid")
    unit: str = Field(..., name="Eenheid")

    class Config:
        orm_mode = True


class GetRecipeListResponseSchema(BaseModel):
    """
    Schema for the response of a list of recipes.

    Attributes
    ----------
    recipe_id : int
        The ID of the recipe.
    """

    recipe_id: int = Field(..., description="ID")

    class Config:
        orm_mode = True
