from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings

SECRET = settings.secret_key
ALGO = "HS256"
ACCESS_TTL = 15  # days
REFRESH_TTL = 30 # days

def _make_token(sub: str, exp_secs: int) -> str:
    now = datetime.now()
    payload = {"sub": sub, "iat": now, "exp": now + timedelta(seconds=exp_secs)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def create_access_token(sub: str) -> str:
    return _make_token(sub, ACCESS_TTL * 24 * 3600)

def create_refresh_token(sub: str) -> str:
    return _make_token(sub, REFRESH_TTL * 24 * 3600)

def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=[ALGO])
