from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class Provider(str, Enum):
    GOOGLE = "GOOGLE"
    GITHUB = "GITHUB"


class OAuthRequest(BaseModel):
    third_party_app: Provider = Field(
        alias="thirdPartyApp", description="OAuth Provider"
    )
    auth_token: str = Field(
        alias="authToken", description="Provider access_token / id_token"
    )

    class Config:
        validate_by_name = True


class LoginPayload(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    message: str


class OTPPayload(LoginPayload):
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class Tokens(BaseModel):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    token_type: str = Field(alias="tokenType", default="bearer")


class ProfileResponse(BaseModel):
    id: int
    uuid: str
    username: str
    email: str
    first_name: str
    last_name: str
    phone_no: str
    email: str
    photo: str | None
    date_joined: str
    user_role: str


class ProfileUpdateResponse(BaseModel):
    message: str
