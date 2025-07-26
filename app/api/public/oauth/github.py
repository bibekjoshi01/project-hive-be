import httpx

from app.api.public.oauth.constants import AuthProviders
from .base import OAuthProvider


class GitHubOAuth(OAuthProvider):
    @staticmethod
    async def validate(token: str) -> dict:
        """
        Validate GitHub OAuth token (which is authorization code here),
        exchange for access token, then fetch user info and emails.
        Return user info dict with keys: email, first_name, last_name, photo, type
        """
        provider_settings = OAuthProvider._get_provider_settings("github")
        client_id = provider_settings["client_id"]
        client_secret = provider_settings["client_secret"]

        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Exchange code for access token
                token_response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "code": token,
                    },
                )
                token_response.raise_for_status()
                token_data = token_response.json()

                access_token = token_data.get("access_token")
                if not access_token:
                    return {"type": "error", "message": "No access token in response"}

                # Step 2: Fetch user profile
                user_response = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                user_response.raise_for_status()
                user_data = user_response.json()

                # Step 3: Fetch user emails
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                emails_response.raise_for_status()
                emails = emails_response.json()

                primary_email = next(
                    (
                        email["email"]
                        for email in emails
                        if email.get("primary") and email.get("verified")
                    ),
                    None,
                )
                if not primary_email and emails:
                    primary_email = emails[0]["email"]

                if not primary_email:
                    return {"type": "error", "message": "Email not found"}

                # Prepare user info dictionary
                user_info = {
                    "type": "success",
                    "provider": AuthProviders.GITHUB.value,
                    "email": primary_email,
                    "first_name": (
                        user_data.get("name", "").split(" ")[0]
                        if user_data.get("name")
                        else ""
                    ),
                    "last_name": (
                        " ".join(user_data.get("name", "").split(" ")[1:])
                        if user_data.get("name")
                        else ""
                    ),
                    "photo": "",
                }

                return user_info

            except httpx.HTTPStatusError as e:
                return {"type": "error", "message": f"HTTP error: {str(e)}"}
            except Exception as e:
                return {"type": "error", "message": f"Unexpected error: {str(e)}"}
