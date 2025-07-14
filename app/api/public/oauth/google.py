import requests
from requests.exceptions import RequestException
from fastapi import HTTPException

# Custom Imports
from .base import OAuthProvider
from .constants import AuthProviders, UserInfo
from .loggers import auth_logger as logger
from .messages import ERROR_MESSAGES


def raise_value_error(message: str):
    raise ValueError(message) from None


class GoogleOAuth(OAuthProvider):
    """
    Google OAuth provider class for validating authentication tokens
    and retrieving user information.
    """

    INFO_API = "https://oauth2.googleapis.com/tokeninfo"
    USER_INFO_API = "https://www.googleapis.com/oauth2/v3/userinfo"

    @classmethod
    def validate(cls, auth_token: str) -> UserInfo | dict:
        """
        Validates an authentication token and retrieves user information.

        Args:
            auth_token (str): The authentication token to validate.

        Returns:
            dict: A dictionary containing user information or an error message.

        Raises:
            ValueError: If the auth token is missing or invalid.
            RequestException: If there's an issue with the API request.
            KeyError: If the expected fields are missing in the API response.
        """
        if not cls.INFO_API or not cls.USER_INFO_API:
            error_message = (
                "Subclasses must define token_info_api and user_info_api.",
            )
            raise NotImplementedError(error_message)

        if not auth_token:
            error_message = "Please provide auth token."
            raise HTTPException(400, error_message)

        google_settings = cls._get_provider_settings("google")

        try:
            # Validate the token with the provider's token API
            token_response = requests.get(
                cls.INFO_API,
                params={"access_token": auth_token},
                timeout=10,
            )
            token_response.raise_for_status()
            token_info = token_response.json()

            # Check if the audience is valid (web, android, or iOS)
            if token_info.get("aud") not in google_settings["client_id"]:
                error_message = "Invalid token: Audience does not match client_id."
                raise_value_error(error_message)

            # Retrieve user information
            user_response = requests.get(
                cls.USER_INFO_API,
                params={"access_token": auth_token},
                timeout=10,
            )
            user_response.raise_for_status()
            user_info = user_response.json()

            image_url = user_info.get("picture")

            # Download the image
            if image_url:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()

            # Format and return user info
            return {
                "type": "success",
                "provider": AuthProviders.GOOGLE.value,
                "first_name": user_info.get("given_name", ""),
                "last_name": user_info.get("family_name", ""),
                "full_name": user_info.get("name", ""),
                "photo": None, # FIXME
                "email": user_info.get("email").strip().lower(),
            }

        except RequestException as err:
            logger.error(f"Failed to fetch user information from Google API: {err}")
            raise raise_value_error(ERROR_MESSAGES["request_failed"]) from err
        except Exception as err:
            logger.error(f"Unexpected error occurred: {err}")
            raise ValueError(ERROR_MESSAGES["signin_failed"]) from err
