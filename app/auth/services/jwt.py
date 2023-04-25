from api.auth.v1.response.auth import TokensSchema
from core.exceptions.base import UnauthorizedException
from core.exceptions.token import DecodeTokenException
from core.helpers.hashid import decode_single, encode
from core.utils.token_checker import token_checker
from core.utils.token_helper import TokenHelper


class JwtService:
    async def verify_token(self, token: str) -> None:
        TokenHelper.decode(token=token)

    async def create_refresh_token(
        self,
        access_token: str,
        refresh_token: str,
    ) -> TokensSchema:
        access_token = TokenHelper.decode(token=access_token)
        refresh_token = TokenHelper.decode(token=refresh_token)

        if refresh_token.get("token_id") is None:
            raise DecodeTokenException

        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException

        user_id = decode_single(access_token.get("user_id"))
        user_id = encode(user_id)

        try:
            token_id = token_checker.generate_add(refresh_token.get("token_id"))
        except ValueError as e:
            raise UnauthorizedException
        except KeyError as e:
            raise DecodeTokenException
            
        return TokensSchema(
            access_token=TokenHelper.encode(
                payload={"user_id": access_token.get("user_id")}
            ),
            refresh_token=TokenHelper.encode(
                payload={"sub": "refresh", "token_id": token_id}
            ),
        )

    async def create_login_tokens(user_id: int):
        user_id = encode(int(user_id))

        return TokensSchema(
            access_token=TokenHelper.encode(payload={"user_id": user_id}),
            refresh_token=TokenHelper.encode(
                payload={"sub": "refresh", "token_id": token_checker.generate_add()}
            ),
        )
