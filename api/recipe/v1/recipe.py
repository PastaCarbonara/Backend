from typing import List, Dict, Union, Annotated

from fastapi import APIRouter, Depends, Query, Request, Form, File, UploadFile
from fastapi.responses import PlainTextResponse
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.recipe.schemas import (
    JudgeRecipeRequestSchema,
    GetRecipeListResponseSchema,
    GetFullRecipeResponseSchema,
    UserCreateRecipeRequestSchema,
    CreatorCreateRecipeRequestSchema,
    CreateRecipeIngredientSchema,
)
from app.recipe.services import RecipeService
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    ProvidesUserID,
    IsAdmin,
)


recipe_v1_router = APIRouter()


@recipe_v1_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GetFullRecipeResponseSchema],
)
@version(1)
async def get_recipe_list():
    return await RecipeService().get_recipe_list()


@recipe_v1_router.get(
    "/{recipe_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GetFullRecipeResponseSchema,
)
@version(1)
async def get_recipe_by_id(recipe_id: int):
    return await RecipeService().get_recipe_by_id(recipe_id)


@recipe_v1_router.put(
    "/{recipe_id}/judge",
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll, ProvidesUserID]))],
)
@version(1)
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema):
    await RecipeService().judge_recipe(recipe_id, **request.dict())
    return "Ok"


@recipe_v1_router.post(
    "",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin, ProvidesUserID]))],
)
@version(1)
async def create_recipe(request: UserCreateRecipeRequestSchema):
    recipe_id = await RecipeService().create_recipe(
        CreatorCreateRecipeRequestSchema(creator_id=request.user_id, **request.dict())
    )
    return await RecipeService().get_recipe_by_id(recipe_id)


def form_to_schema(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    preparing_time: Annotated[int, Form()],
    image: Annotated[str, Form()],
    user_id: Annotated[int, Form()],
    tags: Annotated[List[int], Form()],
    instructions: Annotated[List[str], Form()],
    ingredients: Annotated[List[Dict[str, Union[int, float, str]]], Form()],
) -> UserCreateRecipeRequestSchema:
    return UserCreateRecipeRequestSchema(
        name=name,
        description=description,
        preparing_time=preparing_time,
        image=image,
        user_id=user_id,
        tags=tags,
        instructions=instructions,
        ingredients=ingredients,
    )


@recipe_v1_router.post(
    "/test",
    responses={"400": {"model": ExceptionResponseSchema}},
    # dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
@version(1)
async def endpoint(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    preparing_time: Annotated[int, Form()],
    image: Annotated[str, Form()],
    user_id: Annotated[int, Form()],
    tags: Annotated[List[int], Form()],
    instructions: Annotated[List[str], Form()],
    ingredients: Annotated[List[Dict[str, Union[int, float, str]]], Form()],
    image_file: UploadFile = File(...),
):
    print(name)
    # validate recipe data
    create_recipe_schema = UserCreateRecipeRequestSchema(
        name=name,
        description=description,
        preparing_time=preparing_time,
        image=image,
        user_id=user_id,
        tags=tags,
        instructions=instructions,
        ingredients=ingredients,
    )

    # upload image to azure and get the link of uploaded image

    # save recipe data in database
    # with open("image.jpg", "wb") as image:
    #     image.write(image_file)
    #     image.close()

    return create_recipe_schema
