import uuid
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from .utils.generate_username import generate_username
from app.database import execute_query, perform_query

from .utils.send_otp import send_otp_email
from .schemas.auth import LoginPayload, LoginResponse

router = APIRouter(prefix="/auth")


def get_user_by_email(email: str):
    query = f"SELECT id, username FROM \"user\" WHERE email = '{email}' AND NOT is_archived;"
    rows = perform_query(query)
    return rows[0] if rows else None


def create_user(email: str, username: str, role="VISITOR"):
    now = datetime.now().isoformat()
    query = f"""
    INSERT INTO "user" (
        uuid, username, first_name, last_name, phone_no, user_role,
        email, is_active, is_archived, date_joined, updated_at
    )
    VALUES (
        '{uuid.uuid4()}', '{username}', '', '', '', '{role}',
        '{email}', TRUE, FALSE, '{now}', '{now}'
    )
    RETURNING id;
    """
    return execute_query(query)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(payload: LoginPayload):
    user = get_user_by_email(payload.email)
    if user:
        user_id = user['id']
    else:
        username = generate_username(payload.email)
        user_id = create_user(payload.email, username)

    try:
        send_otp_email(payload.email, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {e}")

    return {"message": "OTP Sent to your mail"}
