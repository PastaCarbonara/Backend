from fastapi import APIRouter, Response, Depends
from app.swipe_session_recipe_queue.services.swipe_session_recipe_queue import SwipeSessionRecipeQueueService

from core.fastapi.dependencies import PermissionDependency, AllowAll

home_router = APIRouter()


@home_router.get("/health", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def home():
    return Response(status_code=200)

@home_router.get("/test", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def test():
    return await SwipeSessionRecipeQueueService().create_queue(2)