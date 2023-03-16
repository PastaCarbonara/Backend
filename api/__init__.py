from fastapi import APIRouter

from api.user.v1.user import user_router as user_v1_router
from api.auth.auth import auth_router
from api.recipe.v1.recipe import recipe_router

router = APIRouter()
router.include_router(user_v1_router, prefix="/api/v1/users", tags=["User"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(recipe_router, prefix="/api/v1/recipes", tags=["Recipe"])


__all__ = ["router"]
