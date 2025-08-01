from fastapi import APIRouter, Depends, HTTPException, status

from .schemas.auth import LoginPayload, LoginResponse
from app.utils._jwt import create_access_token, create_refresh_token
from app.utils.user import get_user_by_email, verify_password


router = APIRouter(prefix="/auth-app")


@router.post("/login", response_model=LoginResponse, status_code=200)
def login(user_info: LoginPayload):

    user = get_user_by_email(user_info.email)

    # Check user password

    if user:
        if not verify_password(user["id"], user_info.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or password"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email"
        )

    access = create_access_token(str(user["id"]))
    refresh = create_refresh_token(str(user["id"]))

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "full_name": user["full_name"],
        "role": "ADMIN",
    }
