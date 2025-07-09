from pydantic import BaseModel, EmailStr


class LoginPayload(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    message: str