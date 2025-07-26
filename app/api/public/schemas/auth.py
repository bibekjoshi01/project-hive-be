from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

from app.utils.casing import CamelBaseModel


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


class LoginPayload(CamelBaseModel):
    email: EmailStr


class EmailLoginResponse(CamelBaseModel):
    message: str


class OTPPayload(CamelBaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class LoginResponse(CamelBaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    full_name: str
    role: str
    photo: Optional[str]


class ProfileResponse(CamelBaseModel):
    id: int
    uuid: str
    username: str
    email: str
    bio: Optional[str]
    first_name: str
    last_name: str
    phone_no: str
    email: str
    photo: str | None
    date_joined: str
    user_role: str


class ProfileUpdateResponse(BaseModel):
    message: str


class MyProjectOut(CamelBaseModel):
    id: int
    title: str
    slug: str
    status: str
    submitted_at: str
    category_name: Optional[str] = None


class MyProjectList(CamelBaseModel):
    count: int
    results: List[MyProjectOut]
