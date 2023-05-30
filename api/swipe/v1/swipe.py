# pylint: skip-file

from typing import List

from fastapi import APIRouter, Depends, Query, Request, WebSocket
from app.swipe.schemas.swipe import CreateSwipeSchema, SwipeSchema
from app.swipe.services.swipe import SwipeService

from core.exceptions.responses import ExceptionResponseSchema
from core.fastapi.dependencies import (
    AllowAll,
    IsAdmin,
    PermissionDependency,
)
from core.fastapi_versioning.versioning import version


swipe_v1_router = APIRouter()


# @swipe_v1_router.post(
#     "",
#     response_model=SwipeSchema,
#     responses={"400": {"model": ExceptionResponseSchema}},
#     dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
# )
# @version(1)
# async def create_swipe(request: CreateSwipeSchema):
#     swipe_id = await SwipeService().create_swipe(request)
#     return await SwipeService().get_swipe_by_id(swipe_id)
