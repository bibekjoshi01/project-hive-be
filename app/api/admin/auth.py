from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import get_current_admin_user

from .schemas.auth import LoginPayload, LoginResponse, ProfileResponse
from app.utils._jwt import create_access_token, create_refresh_token
from app.utils.user import get_user_by_email, get_user_data_by_id, verify_password


router = APIRouter(prefix="/auth-app")


@router.post("/login", response_model=LoginResponse, status_code=200)
def login(user_info: LoginPayload):

    user = get_user_by_email(user_info.email, check_admin=True)

    if user:
        if not verify_password(user["id"], user_info.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
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


@router.get("/profile", response_model=ProfileResponse)
async def profile(
    request: Request, current_user: dict = Depends(get_current_admin_user)
):

    user_data = get_user_data_by_id(current_user["id"])

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_data["date_joined"] = user_data["date_joined"].isoformat()
    user_data["bio"] = user_data.get("bi0", "")
    user_data["photo"] = user_data.get("photo", "")

    return user_data
