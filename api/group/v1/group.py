import json
from typing import List

from pydantic import ValidationError
from app.group.schemas.group import GroupSchema, UserCreateGroupSchema
from app.group.services.group import GroupService

from fastapi import APIRouter, Depends, Query, Request
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version


from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    ProvidesUserID,
    IsAdmin,
    IsAuthenticated,
)


group_v1_router = APIRouter()


@group_v1_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GroupSchema],
    dependencies=[Depends(PermissionDependency([IsAdmin]))]
)
@version(1)
async def get_group_list():
    return await GroupService().get_group_list()


@group_v1_router.post(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GroupSchema,
    dependencies=[Depends(PermissionDependency([ProvidesUserID, IsAuthenticated]))]
)
@version(1)
async def create_group(request: UserCreateGroupSchema):
    group_id = await GroupService().create_group(request)
    return await GroupService().get_group_by_id(group_id)
