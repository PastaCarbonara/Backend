from fastapi import APIRouter, Response, Depends

from core.fastapi.dependencies import PermissionDependency, AllowAll

home_router = APIRouter()


XXX = 2

@home_router.get("/health", dependencies=[Depends(PermissionDependency([[AllowAll]]))])
async def home():
    return Response(status_code=200)
