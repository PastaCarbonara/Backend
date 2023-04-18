from fastapi import APIRouter, Depends
from app.group.schemas.group import GroupSchema
from app.group.services.group import GroupService
from app.user.schemas.user import UserSchema
from core.fastapi.dependencies.permission import IsAuthenticated, PermissionDependency
from core.fastapi.dependencies.user import get_current_user
from core.fastapi_versioning.versioning import version


me_v1_router = APIRouter()


@me_v1_router.get(
    "",
    response_model=UserSchema,
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))]
)
@version(1)
async def get_me(user = Depends(get_current_user)):
    return user


@me_v1_router.get(
    "/groups",
    response_model=list[GroupSchema],
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))]
)
@version(1)
async def get_user_groups(user: int = Depends(get_current_user)):
    return await GroupService().get_groups_by_user(user.id)
