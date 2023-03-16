from pydantic import BaseModel, Field


class RefreshTokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
