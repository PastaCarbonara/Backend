from typing import List

from fastapi import APIRouter, Depends, Query, Request
from core.fastapi_versioning import version

from app.recipe.schemas import (
    ExceptionResponseSchema,
)


recipe_v2_router = APIRouter()


@recipe_v2_router.get(    
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=str,
)
@version(2)
async def get_recipe_list():
    return "lmao"