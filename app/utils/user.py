import uuid
from typing import List
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.database import execute_query, perform_query


def get_user_by_email(email: str, check_admin=False):
    # Base query
    query = """
    SELECT 
        id, 
        username, 
        first_name || ' ' || last_name AS full_name, 
        photo 
    FROM "user" 
    WHERE email = %s AND NOT is_archived
    """

    params = [email]

    if check_admin:
        query += " AND user_role IN ('ADMIN', 'STAFF')"

    rows = perform_query(query, params)
    return rows[0] if rows else None


def get_user_by_id(id: str):
    query = f"SELECT id, username, user_role FROM \"user\" WHERE id = '{id}' AND NOT is_archived;"
    rows = perform_query(query)
    return rows[0] if rows else None


def create_user(
    email: str,
    username: str,
    firstname: str = "",
    lastname: str = "",
    role="VISITOR",
    conn=None,
):
    now = datetime.now().isoformat()
    query = """
    INSERT INTO "user" (
        uuid, username, first_name, last_name, phone_no, user_role,
        email, is_active, is_archived, date_joined, updated_at
    )
    VALUES (
        %s, %s, %s, %s, %s, %s,
        %s, TRUE, FALSE, %s, %s
    )
    RETURNING id;
    """
    params = (
        str(uuid.uuid4()),
        username,
        firstname,
        lastname,
        "",
        role,
        email,
        now,
        now,
    )
    return execute_query(query, params, conn)


def update_user_profile(set_clauses: List, params: List):
    query = f"""
        UPDATE "user"
        SET {', '.join(set_clauses)}, updated_at = now()
        WHERE id = %s;
    """
    return execute_query(query, tuple(params))


def verify_otp(user_id: int, otp: str) -> bool:
    OTP_LIFETIME = timedelta(minutes=settings.otp_lifetime)

    select_sql = """
        SELECT id, created_at
        FROM user_verification
        WHERE user_id = %s AND otp = %s
        LIMIT 1;
    """
    rows = perform_query(select_sql, (user_id, otp))
    is_valid = False

    if rows:
        created_at = rows[0]["created_at"]
        expires_at = created_at + OTP_LIFETIME
        now_utc = datetime.now(timezone.utc)
        is_valid = expires_at > now_utc

    delete_sql = "DELETE FROM user_verification WHERE user_id = %s;"
    execute_query(delete_sql, (user_id,))

    return is_valid


def verify_password(user_id: int, password: str) -> bool:

    select_sql = """
        SELECT id
        FROM "user"
        WHERE id = %s AND password = %s
        LIMIT 1;
    """
    rows = perform_query(select_sql, (user_id, password))
    if rows:
        return True

    return False


def get_user_data_by_id(user_id: int) -> dict | None:
    query = """
        SELECT id, email, uuid, photo, bi0, username, first_name, last_name, phone_no, user_role, date_joined
        FROM "user"
        WHERE id = %s AND NOT is_archived
        LIMIT 1;
    """
    rows = perform_query(query, (user_id,))

    if rows:
        return rows[0]

    return None
