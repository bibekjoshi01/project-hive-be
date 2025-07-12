from pydantic import BaseModel, EmailStr, Field


class LoginPayload(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    message: str


class OTPPayload(LoginPayload):
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"