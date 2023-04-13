from fastapi import Request
from app.user.repository.user import UserRepository


async def get_current_user(request: Request):
    user = request.user
    
    if not user: return None
    if not user.id: return None

    return await UserRepository().get_user_by_id(user.id)
