from app.config import settings

from .loggers import auth_logger as logger


class OAuthProvider:
    """
    Base class for OAuth providers.
    """

    GOOGLE_CLIENT_ID = settings.google_client_id
    GOOGLE_CLIENT_SECRET = settings.google_client_secret
    GITHUB_CLIENT_ID = settings.github_client_id
    GITHUB_CLIENT_SECRET = settings.github_client_secret

    @staticmethod
    def _get_provider_settings(provider_name: str) -> dict[str, str]:
        """
        Retrieves the OAuth provider settings.

        Returns:
            Dict[str, str]: The provider settings containing \
                client_id and client_secret.

        Raises:
            ValueError: If the provider settings are not found or invalid.
        """

        mapping = {
            "google": {
                "client_id": OAuthProvider.GOOGLE_CLIENT_ID,
                "client_secret": OAuthProvider.GOOGLE_CLIENT_SECRET,
            },
            "github": {
                "client_id": OAuthProvider.GITHUB_CLIENT_ID,
                "client_secret": OAuthProvider.GITHUB_CLIENT_SECRET,
            },
        }

        provider_settings = mapping.get(provider_name, {})

        if not provider_settings:
            error_message = (
                f"{provider_name.capitalize()} "
                "OAuth settings are not configured in 'settings.oauth_providers'",
            )
            logger.error(error_message)
            raise ValueError(error_message)

        if not provider_settings.get("client_id") or not provider_settings.get(
            "client_secret",
        ):
            error_message = (
                f"{provider_name.capitalize()} "
                "Auth settings must include 'client_id' and 'client_secret'."
            )
            logger.error(error_message)
            raise ValueError(error_message)

        return provider_settings
