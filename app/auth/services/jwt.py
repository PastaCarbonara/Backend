"""
Class business logic for json web tokens
"""

from api.auth.v1.response.auth import TokensSchema
from core.exceptions.base import UnauthorizedException
from core.exceptions.token import DecodeTokenException
from core.helpers.hashid import decode_single, encode
from core.utils.token_checker import token_checker
from core.utils.token_helper import TokenHelper


class JwtService:
    """
    Class for JSON Web Token business logic
    """

    async def verify_token(self, token: str) -> None:
        """
        Verify the given token

        Args:
            token (str): The token to verify

        Raises:
            DecodeTokenException: If the token cannot be decoded
        """
        TokenHelper.decode(token=token)

    async def create_refresh_token(
        self,
        access_token: str,
        refresh_token: str,
    ) -> TokensSchema:
        """
        Create a new refresh token

        Args:
            access_token (str): The access token to include in the new refresh token
            refresh_token (str): The old refresh token to use as a template for the new 
            refresh token

        Returns:
            TokensSchema: A new set of tokens containing the new access token and refresh token

        Raises:
            DecodeTokenException: If the old refresh token cannot be decoded
            UnauthorizedException: If the new token ID cannot be generated
        """
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

        except ValueError as exc:
            raise UnauthorizedException from exc

        except KeyError as exc:
            raise DecodeTokenException from exc

        return TokensSchema(
            access_token=TokenHelper.encode(
                payload={"user_id": access_token.get("user_id")}
            ),
            refresh_token=TokenHelper.encode(
                payload={"sub": "refresh", "token_id": token_id}
            ),
        )

    async def create_login_tokens(self, user_id: int):
        """
        Create a new set of access and refresh tokens for the given user

        Args:
            user_id (int): The ID of the user to create tokens for

        Returns:
            TokensSchema: A new set of tokens containing the access and refresh tokens
        """
        user_id = encode(int(user_id))

        return TokensSchema(
            access_token=TokenHelper.encode(payload={"user_id": user_id}),
            refresh_token=TokenHelper.encode(
                payload={"sub": "refresh", "token_id": token_checker.generate_add()}
            ),
        )
