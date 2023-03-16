from fastapi import APIRouter

from api.user.v1.user import user_router as user_v1_router
from api.auth.v1.auth import auth_v1_router
from api.recipe.v1.recipe import recipe_v1_router
from api.recipe.v2.recipe import recipe_v2_router

router = APIRouter()
router.include_router(user_v1_router, prefix="/users", tags=["User"])
router.include_router(auth_v1_router, prefix="/auth", tags=["Auth"])
router.include_router(recipe_v1_router, prefix="/recipes", tags=["Recipe"])
router.include_router(recipe_v2_router, prefix="/recipes", tags=["Recipe"])


__all__ = ["router"]
