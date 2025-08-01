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
