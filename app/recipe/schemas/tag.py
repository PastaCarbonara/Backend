from pydantic import BaseModel, Field, root_validator
from pydantic.utils import GetterDict
from app.tag.schemas.tag import Tag


class RecipeTagSchema(BaseModel):
    tag: Tag = Field(..., description="Tag information object")

    class Config:
        orm_mode = True


class FlattendRecipeTagSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Tag name")

    @root_validator(pre=True)
    def flatten_recipe_tag(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        tag = values.get("tag")
        if tag is None:
            return values
        tag = Tag.validate(tag)
        return {
            "id": tag.id,
            "name": tag.name,
        } | dict(values)

    class Config:
        orm_mode = True
