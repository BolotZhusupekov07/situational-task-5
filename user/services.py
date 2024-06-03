import base64
from datetime import timedelta
from http.client import HTTPException
import time
from typing import Any, Optional

import jwt
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

from user.models import OAuthAccount, User
from cryptography.fernet import Fernet

JWT_ALGORITHM = "HS256"


def generate_jwt(
    data: dict,
    secret: str,
    lifetime_seconds: Optional[int] = None,
    algorithm: str = JWT_ALGORITHM,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expire = timezone.now() + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str,
    secret: str,
    audience: list[str],
) -> dict[str, Any]:
    return jwt.decode(
        encoded_jwt,
        secret,
        audience=audience,
        options={
            "verify_signature": False,
            "verify_iss": True,
            "verify_aud": True,
            "verify_exp": True,
        },
    )



def get_google_oauth_client(
    request: HttpRequest, redirect_url: str
) -> OAuth2Client:
    google_oauth_adapter = GoogleOAuth2Adapter
    return OAuth2Client(
        request,
        settings.GOOGLE_OAUTH_CLIENT_ID,
        settings.GOOGLE_OAUTH_CLIENT_SECRET,
        google_oauth_adapter.access_token_method,
        google_oauth_adapter.access_token_url,
        redirect_url,
    )

def get_token_expires_at(token_dict: dict[str, Any]) -> int | None:
    expires_at = None
    if "expires_at" in token_dict:
        expires_at = int(token_dict["expires_at"])
    elif "expires_in" in token_dict:
        expires_at = int(time.time()) + int(token_dict["expires_in"])
    return expires_at

def get_google_oauth_account_data(
    access_token_dict: dict[str, Any], id_token_dict: dict[str, Any]
) -> dict[str, Any]:
    return {
        "oauth_name": settings.GOOGLE_OAUTH_NAME,
        "access_token": access_token_dict.get("access_token"),
        "account_id": id_token_dict.get("sub"),
        "account_email": id_token_dict.get("email"),
        "expires_at": get_token_expires_at(access_token_dict),
    }


def get_google_user_data(
    id_token_dict: dict[str, Any]
) -> dict[str, Any | None]:
    return {
        "email": id_token_dict.get("email"),
        "avatar": id_token_dict.get("picture", ""),
        "first_name": id_token_dict.get("given_name", ""),
        "last_name": id_token_dict.get("family_name", ""),
    }


def decode_google_id_token(id_token: str) -> dict[str, Any]:
    audience = []
    if settings.GOOGLE_OAUTH_CLIENT_ID:
        audience.append(settings.GOOGLE_OAUTH_CLIENT_ID)

    return decode_jwt(
        id_token,
        settings.SOCIAL_AUTH_SECRET,
        audience,
    )


def get_google_user_and_oauth_account_dict(
    request: HttpRequest, code: str | None, redirect_url: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    client = get_google_oauth_client(request, redirect_url)
    token_dict = client.get_access_token(code)
    id_token_dict = decode_google_id_token(token_dict["id_token"])
    user_dict = get_google_user_data(id_token_dict)
    oauth_account_dict = get_google_oauth_account_data(
        token_dict, id_token_dict
    )
    return user_dict, oauth_account_dict


def create_user_object_from_oauth(
    email: str, user_dict: dict[str, str]
) -> User:
    user = User.objects.filter(email=email).first()
    if user:
        return user

    return User.objects.create_user(
        email=email,
        password=None,
        first_name=user_dict.get("first_name", ""),
        last_name=user_dict.get("last_name", ""),
    )


class TokenCryptography:
    def __init__(self):
        self.fernet = Fernet(self._get_secret_key())

    @staticmethod
    def _get_secret_key():
        if not settings.SECRET_TOKEN_KEY:
            return Fernet.generate_key()
        return base64.b64decode(settings.SECRET_TOKEN_KEY)

    def encode_token(self, token: str) -> str:
        return self.fernet.encrypt(token.encode())

    def decode_token(self, encrypted_token: str) -> str:
        return self.fernet.decrypt(encrypted_token).decode()



def encode_access_and_refresh_tokens(
    access_token: str | None, refresh_token: str | None
) -> tuple[str, str]:
    token_cryptography = TokenCryptography()
    encrypted_access_token = ""
    if access_token:
        encrypted_access_token = token_cryptography.encode_token(access_token)

    encrypted_refresh_token = ""
    if refresh_token:
        encrypted_refresh_token = token_cryptography.encode_token(
            refresh_token
        )

    return encrypted_access_token, encrypted_refresh_token


def create_user_oauth_account(
    user: User, oauth_account_dict: dict[str, str | int | None]
) -> OAuthAccount:
    access_token = oauth_account_dict.get("access_token")
    refresh_token = oauth_account_dict.get("refresh_token")
    (
        encrypted_access_token,
        encrypted_refresh_token,
    ) = encode_access_and_refresh_tokens(
        str(access_token) if access_token else None,
        str(refresh_token) if refresh_token else None,
    )

    return OAuthAccount.objects.create(
        user=user,
        oauth_name=str(oauth_account_dict.get("oauth_name")),
        access_token=encrypted_access_token,
        refresh_token=encrypted_refresh_token,
        expires_at=oauth_account_dict.get("expires_at"),
        account_id=str(oauth_account_dict.get("account_id")),
        account_email=oauth_account_dict.get("account_email"),
    )


@transaction.atomic
def create_user_from_oauth(
    user_dict: dict[str, str],
    oauth_account_dict: dict[str, Any],
) -> User:
    user = create_user_object_from_oauth(user_dict.get('email'), user_dict)
    create_user_oauth_account(user, oauth_account_dict)

    return user


def update_user_oauth_account(
    user: User, oauth_account_dict: dict[str, str | int]
) -> OAuthAccount:
    oauth_account = OAuthAccount.objects.get(
        user=user, oauth_name=oauth_account_dict["oauth_name"]
    )
    access_token = oauth_account_dict.get("access_token")
    refresh_token = oauth_account_dict.get("refresh_token")
    expires_at = oauth_account_dict.get("expires_at")
    (
        encrypted_access_token,
        encrypted_refresh_token,
    ) = encode_access_and_refresh_tokens(
        str(access_token) if access_token else None,
        str(refresh_token) if refresh_token else None,
    )
    oauth_account.update_account(
        access_token=encrypted_access_token,
        expires_at=int(expires_at) if expires_at else 0,
        refresh_token=encrypted_refresh_token,
    )
    return oauth_account


def oauth_login(
    user_dict: dict[str, str], oauth_account_dict: dict[str, Any]
) -> User:
    user = OAuthAccount.objects.filter(
        oauth_name=oauth_account_dict["oauth_name"],
        account_id=oauth_account_dict["account_id"]
    ).first().user
    if not user:
        user = create_user_from_oauth(user_dict, oauth_account_dict)
    else:
        update_user_oauth_account(user, oauth_account_dict)
    return user


def google_oauth_login(
    user_dict: dict[str, str], oauth_account_dict: dict[str, Any]
) -> User:
    user = User.objects.filter(email=user_dict.get('email')).first()
    if user:
        oauth_account = OAuthAccount.objects.filter(
            oauth_name=oauth_account_dict["oauth_name"],
            account_id=oauth_account_dict["account_id"]
        ).first()
        if oauth_account:
            update_user_oauth_account(user, oauth_account_dict)
        else:
            create_user_oauth_account(user, oauth_account_dict)
    else:
        user = create_user_from_oauth(user_dict, oauth_account_dict)
    return user


def google_auth(
    request: HttpRequest, code: str | None, error: str | None
) -> User:
    if not code or error:
        raise HTTPException('OAUTH2 exception')

    user_dict, oauth_account_dict = get_google_user_and_oauth_account_dict(
        request, code, settings.GOOGLE_API_V1_AUTH_CALLBACK_URL
    )
    return google_oauth_login(user_dict, oauth_account_dict)


def get_google_authorization_url(request: HttpRequest) -> str:
    client = get_google_oauth_client(
        request, settings.GOOGLE_API_V1_AUTH_CALLBACK_URL
    )
    return client.get_redirect_url(settings.GOOGLE_OAUTH_AUTHORIZE_URL, ['profile', 'email'], {})