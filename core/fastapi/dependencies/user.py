"""GET CURRENT USER DEPENDENCY"""

from fastapi import Request
from app.user.repository.user import UserRepository
from core.db.models import User


async def get_current_user(request: Request) -> User:
    """
    Get current user from request.

    Parameters
    ----------
    request : Request
        Request object.
    
    Returns
    -------
    User
        User object.
    """
    user = request.user

    if not user:
        return None
    if not user.id:
        return None

    return await UserRepository().get_user_by_id(user.id)
