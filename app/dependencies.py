from fastapi import HTTPException, Security, status
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer

# Project Imports
from app.utils._jwt import decode_token
from app.utils.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user = get_user_by_id(int(payload["sub"]))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )
    
    return user
