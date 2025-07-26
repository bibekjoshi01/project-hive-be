import httpx
from fastapi import HTTPException

from app.api.public.oauth.base import OAuthProvider
from .constants import AuthProviders, UserInfo
from .loggers import auth_logger as logger
from .messages import ERROR_MESSAGES


class GoogleOAuth(OAuthProvider):
    INFO_API = "https://oauth2.googleapis.com/tokeninfo"
    USER_INFO_API = "https://www.googleapis.com/oauth2/v3/userinfo"

    @classmethod
    async def validate(cls, auth_token: str) -> UserInfo | dict:
        if not auth_token:
            raise HTTPException(400, "Please provide auth token.")

        google_settings = cls._get_provider_settings("google")

        async with httpx.AsyncClient() as client:
            try:
                # Validate the token with the provider's token API
                token_response = await client.get(
                    cls.INFO_API,
                    params={"access_token": auth_token},
                    timeout=10,
                )
                token_response.raise_for_status()
                token_info = token_response.json()

                # Check audience matches client_id(s)
                if token_info.get("aud") not in google_settings["client_id"]:
                    raise HTTPException(
                        400, "Invalid token: Audience does not match client_id."
                    )

                # Retrieve user information
                user_response = await client.get(
                    cls.USER_INFO_API,
                    params={"access_token": auth_token},
                    timeout=10,
                )
                user_response.raise_for_status()
                user_info = user_response.json()

                return {
                    "type": "success",
                    "provider": AuthProviders.GOOGLE.value,
                    "first_name": user_info.get("given_name", ""),
                    "last_name": user_info.get("family_name", ""),
                    "full_name": user_info.get("name", ""),
                    "photo": None,  # FIXME: Add photo handling if needed
                    "email": user_info.get("email", "").strip().lower(),
                }

            except httpx.HTTPStatusError as err:
                logger.error(f"Failed to fetch user information from Google API: {err}")
                raise HTTPException(400, ERROR_MESSAGES["request_failed"]) from err
            except Exception as err:
                logger.error(f"Unexpected error occurred: {err}")
                raise HTTPException(400, ERROR_MESSAGES["signin_failed"]) from err
