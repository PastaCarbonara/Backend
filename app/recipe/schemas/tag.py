from pydantic import BaseModel, Field, root_validator
from pydantic.utils import GetterDict
from app.tag.schema.tag import TagSchema


class RecipeTagSchema(BaseModel):
    tag: TagSchema = Field(..., description="Tag information object")

    class Config:
        orm_mode = True


class CreateRecipeTagSchema(BaseModel):
    id: int


class FlattenedRecipeTagSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Tag name")

    @root_validator(pre=True)
    def flatten_recipe_tag(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        tag = values.get("tag")
        if tag is None:
            return values
        tag = TagSchema.validate(tag)
        return {
            "id": tag.id,
            "name": tag.name,
        } | dict(values)

    class Config:
        orm_mode = True
