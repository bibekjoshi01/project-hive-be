import requests
from requests.exceptions import RequestException
from fastapi import HTTPException

from .base import OAuthProvider


class GitHubOAuth(OAuthProvider): ...
