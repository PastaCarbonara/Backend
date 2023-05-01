import uuid
from api.auth.v1.response.auth import TokensSchema
from app.auth.exceptions.auth import BadUUIDException
from app.auth.services.jwt import JwtService
from app.user.exception.user import IncorrectPasswordException, UserNotFoundException
from app.user.services.user import UserService
from app.user.utils import verify_password


class AuthService:
    def __init__(self) -> None:
        self.jwt = JwtService
        self.user_serv = UserService()

    async def login(self, username: str, password: str) -> TokensSchema:
        user = await self.user_serv.get_user_by_display_name(username)
        if not user:
            raise UserNotFoundException()
        if not verify_password(password, user.account_auth.password):
            raise IncorrectPasswordException()

        return await self.jwt.create_login_tokens(user.id)

    async def client_token_login(self, ctoken) -> TokensSchema:
        try:
            ctoken = uuid.UUID(str(ctoken), version=4)
        except ValueError:
            raise BadUUIDException
        
        user = await self.user_serv.get_user_by_client_token(ctoken=ctoken)
        
        if not user:
            user_id = await self.user_serv.create_user_with_client_token(ctoken=ctoken, display_name=None)
        else:
            user_id = user.id
        
        return await self.jwt.create_login_tokens(user_id)
