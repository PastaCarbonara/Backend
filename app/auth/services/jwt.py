from app.auth.schemas.jwt import RefreshTokenSchema
from app.user.schemas.user import LoginResponseSchema
from core.exceptions.token import DecodeTokenException
from core.helpers.hashid import decode_single, encode
from core.utils.token_helper import TokenHelper


class JwtService:
    async def verify_token(self, token: str) -> None:
        TokenHelper.decode(token=token)

    async def create_refresh_token(
        self,
        access_token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        access_token = TokenHelper.decode(token=access_token)
        refresh_token = TokenHelper.decode(token=refresh_token)
        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException
        
        user_id = decode_single(access_token.get("user_id"))
        user_id = encode(user_id)

        return RefreshTokenSchema(
            access_token=TokenHelper.encode(payload={"user_id": access_token.get("user_id")}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
    
    async def create_login_tokens(user_id: int):
        user_id = encode(int(user_id))

        return LoginResponseSchema(
            access_token=TokenHelper.encode(payload={"user_id": user_id}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
