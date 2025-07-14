from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jose import JWTError
from fastapi import Form, UploadFile, File
from typing import Annotated

# Project Imports
from .oauth.auth_validator import AuthTokenValidator
from app.dependencies import get_current_user
from app.utils._jwt import create_access_token, create_refresh_token, decode_token
from app.utils.generators import generate_username
from app.utils.user import (
    create_user,
    get_user_by_email,
    get_user_data_by_id,
    update_user_profile,
    verify_otp,
)
from app.utils.file_handlers import get_full_url, save_upload_file
from app.utils.send_otp import send_otp_email
from .schemas.auth import (
    LoginPayload,
    LoginResponse,
    OAuthRequest,
    OTPPayload,
    ProfileResponse,
    ProfileUpdateResponse,
    Tokens,
)


router = APIRouter(prefix="/auth-app")


@router.post(
    "/oauth",
    status_code=status.HTTP_200_OK,
    response_model=Tokens,
    summary="Signin with Google/Github",
)
async def oauth(payload: OAuthRequest):
    user_info = await AuthTokenValidator.validate(
        provider=payload.third_party_app.value,
        token=payload.auth_token,
    )

    user_id = None
    user = get_user_by_email(user_info["email"])

    if not user:
        username = generate_username(payload.email)
        user_id = create_user(
            user_info["email"],
            username,
            user_info["first_name"],
            user_info["last_name"],
        )
    else:
        user_id = user["id"]

    # JWT
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    return JSONResponse(
        {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
    )


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(payload: LoginPayload):
    user = get_user_by_email(payload.email)
    if user:
        user_id = user["id"]
    else:
        username = generate_username(payload.email)
        user_id = create_user(payload.email, username)

    try:
        send_otp_email(payload.email, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to send OTP: {e}"
        )

    return JSONResponse({"message": "OTP Sent to your mail"})


@router.post("/verify-otp", response_model=Tokens)
async def verify(payload: OTPPayload):
    user = get_user_by_email(payload.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_otp(user["id"], payload.otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP"
        )

    # JWT
    access = create_access_token(str(user["id"]))
    refresh = create_refresh_token(str(user["id"]))

    return JSONResponse(
        {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
    )


@router.post("/refresh", response_model=Tokens)
async def refresh(request: Request):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload["sub"]
    access = create_access_token(user_id)
    return Response(
        {"access_token": access, "refresh_token": token, "token_type": "bearer"}
    )


@router.get("/profile", response_model=ProfileResponse)
async def profile(request: Request, current_user: dict = Depends(get_current_user)):
    user_data = get_user_data_by_id(current_user["id"])

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_data["date_joined"] = user_data["date_joined"].isoformat()

    if user_data.get("photo"):
        user_data["photo"] = get_full_url(request, user_data["photo"])

    return user_data


@router.patch("/profile/update", response_model=ProfileUpdateResponse)
async def update_profile(
    first_name: Annotated[str | None, Form()] = None,
    last_name: Annotated[str | None, Form()] = None,
    phone_no: Annotated[str | None, Form()] = None,
    photo: Annotated[UploadFile | None, File()] = None,
    current_user: dict = Depends(get_current_user),
):

    data = {
        k: v
        for k, v in {
            "first_name": first_name,
            "last_name": last_name,
            "phone_no": phone_no,
        }.items()
        if v is not None
    }

    if photo:
        data["photo"] = save_upload_file(
            photo, "user/photos", allowed_extensions=[".jpg", ".png", ".jpeg"]
        )  # store relative URL

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided"
        )

    set_clauses = [f"{field} = %s" for field in data]
    params = list(data.values()) + [current_user["id"]]

    update_user_profile(set_clauses, params)

    return JSONResponse({"message": "Profile updated successfully"})
