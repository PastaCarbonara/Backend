import uuid
from api.auth.v1.response.auth import TokensSchema
from app.auth.exceptions.auth import BadEncryptedStringException
from app.auth.services.jwt import JwtService
from app.user.exception.user import IncorrectPasswordException, UserNotFoundException
from app.user.repository.user import UserRepository
from app.user.utils import verify_password
from core.helpers.asymmetric_encryption import Encryption
import binascii


class AuthService:
    def __init__(self) -> None:
        self.encryption = Encryption()
        self.jwt = JwtService
        self.user_repository = UserRepository()

    async def login(self, username: str, password: str) -> TokensSchema:
        user = await self.user_repository.get_user_by_display_name(username)
        if not user:
            raise UserNotFoundException()
        if not verify_password(password, user.account_auth.password):
            raise IncorrectPasswordException()

        return await self.jwt.create_login_tokens(user.id)

    async def client_token_login(self, ctoken):
        try:
            ctoken = self.encryption.decrypt(ctoken)

        except binascii.Error:
            raise BadEncryptedStringException
        
        try:
            ctoken = uuid.UUID(ctoken)
        except ValueError:
            raise BadEncryptedStringException
        
        # store/find in db
        # get user_id
        # return tokens
        
        # return self.get_tokens()
