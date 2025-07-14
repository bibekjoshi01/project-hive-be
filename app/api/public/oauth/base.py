from app.config import settings

from .loggers import auth_logger as logger


class OAuthProvider:
    """
    Base class for OAuth providers.
    """

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

        provider_settings = settings.oauth_providers.get(provider_name, {})

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
