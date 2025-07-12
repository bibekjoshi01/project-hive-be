from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jose import JWTError

# Project Imports
from app.utils._jwt import create_access_token, create_refresh_token, decode_token
from app.utils.generators import generate_username
from app.utils.user import create_user, get_user_by_email, verify_otp
from app.utils.send_otp import send_otp_email
from .schemas.auth import LoginPayload, LoginResponse, OTPPayload, Tokens


router = APIRouter(prefix="/auth")


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


