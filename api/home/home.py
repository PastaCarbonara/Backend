from fastapi import APIRouter, Response, Depends
from app.swipe_session_recipe_queue.services.swipe_session_recipe_queue import SwipeSessionRecipeQueueService

from core.fastapi.dependencies import PermissionDependency, AllowAll

home_router = APIRouter()


XXX = 2

@home_router.get("/health", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def home():
    return Response(status_code=200)

@home_router.get("/test", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def test():
    return await SwipeSessionRecipeQueueService().create_queue(XXX)


@home_router.get("/test2", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def test2():
    return await SwipeSessionRecipeQueueService().get_and_progress_queue(XXX, 1)


@home_router.get("/test3", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def test3(recipe_id: int):
    return await SwipeSessionRecipeQueueService().add_to_queue(XXX, recipe_id)