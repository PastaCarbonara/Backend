from fastapi import APIRouter

from api.user.v1.user import user_v1_router
from api.auth.v1.auth import auth_v1_router
from api.recipe.v1.recipe import recipe_v1_router
from api.swipe_session.v1.swipe_session import swipe_session_v1_router
from api.swipe.v1.swipe import swipe_v1_router

router = APIRouter()
router.include_router(user_v1_router, prefix="/users", tags=["User"])
router.include_router(auth_v1_router, prefix="/auth", tags=["Auth"])
router.include_router(recipe_v1_router, prefix="/recipes", tags=["Recipe"])
router.include_router(swipe_session_v1_router, prefix="/swipe_sessions", tags=["Swipe Session"])
router.include_router(swipe_v1_router, prefix="/swipes", tags=["Swipe"])


__all__ = ["router"]