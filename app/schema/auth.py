from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    username: str = Field(..., min_length=1, description="Full name of the user")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="Full name of the user")
    is_active: bool = Field(True, description="Indicates if the user account is active")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT bearer access token")
    token_type: str = Field("bearer", description="Token scheme type")
    accessToken: str = Field(..., description="JWT access token")
    refreshToken: str = Field(..., description="JWT refresh token")


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(..., description="The refresh token")
