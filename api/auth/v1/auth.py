from fastapi import APIRouter, Response

from api.auth.v1.request.auth import RefreshTokenRequest, VerifyTokenRequest
from api.auth.v1.response.auth import RefreshTokenResponse
from app.auth.services.jwt import JwtService
from app.user.schemas import ExceptionResponseSchema
from core.fastapi_versioning import version

auth_v1_router = APIRouter()


@auth_v1_router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    responses={"400": {"model": ExceptionResponseSchema}},
)
@version(1)
async def refresh_token(request: RefreshTokenRequest):
    token = await JwtService().create_refresh_token(
        access_token=request.token, refresh_token=request.refresh_token
    )
    return {"access_token": token.access_token, "refresh_token": token.refresh_token}


@auth_v1_router.post("/verify")
@version(1)
async def verify_token(request: VerifyTokenRequest):
    await JwtService().verify_token(token=request.token)
    return Response(status_code=200)
