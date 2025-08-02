from typing import Optional
from app.utils.casing import CamelBaseModel


class LoginPayload(CamelBaseModel):
    email: str
    password: str


class LoginResponse(CamelBaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    full_name: str
    role: str


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
