from fastapi import APIRouter, Depends, Response
from app.auth.services.auth import AuthService
from app.user.services.user import UserService
from core.exceptions import ExceptionResponseSchema, DecodeTokenException
from core.fastapi.dependencies.permission import AllowAll, PermissionDependency
from core.fastapi_versioning import version

from api.auth.v1.request.auth import RefreshTokenRequest, UUIDSchema, VerifyTokenRequest
from api.auth.v1.response.auth import EncriptionKeySchema, TokensSchema
from app.auth.services.jwt import JwtService
from api.auth.v1.request.auth import LoginRequest, ClientTokenSchema
from api.auth.v1.response.auth import TokensSchema

auth_v1_router = APIRouter()


@auth_v1_router.post(
    "/refresh",
    response_model=TokensSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))]
)
@version(1)
async def refresh_token(request: RefreshTokenRequest):
    return await JwtService().create_refresh_token(
        access_token=request.access_token, refresh_token=request.refresh_token
    )


@auth_v1_router.post(
    "/verify",
    dependencies=[Depends(PermissionDependency([[AllowAll]]))]
)
@version(1)
async def verify_token(request: VerifyTokenRequest):
    try:
        await JwtService().verify_token(token=request.token)

    except DecodeTokenException:
        return Response(status_code=400)

    except Exception as e:
        print(e)
        return Response(status_code=500)

    else:
        return Response(status_code=200)


@auth_v1_router.post(
    "/login",
    response_model=TokensSchema,
    responses={"404": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))]
)
@version(1)
async def login(request: LoginRequest):
    token = await AuthService().login(
        username=request.username, password=request.password
    )
    return {"access_token": token.access_token, "refresh_token": token.refresh_token}


@auth_v1_router.post(
    "/client-token-login",
    response_model=TokensSchema,
    responses={"404": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))]
)
@version(1)
async def client_token_login(request: ClientTokenSchema):
    return await AuthService().client_token_login(ctoken=request.token)


@auth_v1_router.post(
    "/test-encrypt-token",
    responses={"404": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))]
)
@version(1)
async def encrypt_token_test(request: UUIDSchema):
    return AuthService().encryption.encrypt(str(request.token))


@auth_v1_router.get(
    "/public-key",
    # response_model=EncriptionKeySchema,
    dependencies=[Depends(PermissionDependency([[AllowAll]]))]
)
@version(1)
async def get_public_key():
    return await AuthService().get_public_key()
