from fastapi import HTTPException


# Custom Imports
from .constants import AuthProviders, UserInfo
from .google import GoogleOAuth
from .github import GitHubOAuth
from .messages import ERROR_MESSAGES


def raise_api_exception(message: str):
    raise HTTPException(400, message)


class AuthTokenValidator:
    """
    Token validator for third-party providers
    """

    provider_class_map = {"GOOGLE": GoogleOAuth, "GITHUB": GitHubOAuth}

    @staticmethod
    async def validate(provider: str, token: str) -> UserInfo:
        try:
            if not AuthProviders.is_valid_provider(provider):
                raise_api_exception(ERROR_MESSAGES["provider_not_supported"])
            else:
                auth_provider = AuthTokenValidator.provider_class_map[provider]
                user_info = await auth_provider.validate(token)

                if user_info.get("type") != "success":
                    raise_api_exception(ERROR_MESSAGES["signin_failed"])

                return user_info

        except ValueError as err:
            raise HTTPException(400, {"message": str(err)}) from err
        except (Exception, HTTPException) as err:
            raise HTTPException(400, {"message": str(err)}) from err
