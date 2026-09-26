import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

from .models import OwnerSocialIdentity
from .social_oauth_provider import get_owner_social_oauth_provider_config


@dataclass(frozen=True)
class OwnerSocialOAuthTokenResponse:
    access_token: str
    token_type: str
    expires_in: int | None = None


@dataclass(frozen=True)
class OwnerSocialOAuthProfile:
    provider_user_id: str
    username: str = ""


def _provider_prefix(provider):
    if provider == OwnerSocialIdentity.Provider.FACEBOOK:
        return "OWNER_FACEBOOK_OAUTH_"
    if provider == OwnerSocialIdentity.Provider.INSTAGRAM:
        return "OWNER_INSTAGRAM_OAUTH_"
    raise ValueError("Unsupported Owner social provider.")


def exchange_owner_social_authorization_code(provider, code):
    if not code:
        raise ValueError("OAuth authorization code is required.")

    config = get_owner_social_oauth_provider_config(provider)
    prefix = _provider_prefix(provider)

    client_secret = str(getattr(settings, f"{prefix}CLIENT_SECRET", "") or "").strip()
    if not client_secret:
        raise ValueError("Owner social OAuth client secret is not configured.")

    grant_type = str(
        getattr(settings, f"{prefix}GRANT_TYPE", "authorization_code") or ""
    ).strip()
    if not grant_type:
        raise ValueError("Owner social OAuth grant type is not configured.")

    body = urlencode({
        "client_id": config.client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "redirect_uri": config.redirect_uri,
        "code": code,
    }).encode("utf-8")

    request = Request(
        config.token_endpoint,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise ValueError("Owner social OAuth token exchange failed.") from exc

    access_token = str(payload.get("access_token", "") or "").strip()
    if not access_token:
        raise ValueError("Owner social OAuth token response is invalid.")

    token_type = str(payload.get("token_type", "Bearer") or "Bearer").strip()
    expires_in = payload.get("expires_in")
    if expires_in is not None:
        try:
            expires_in = int(expires_in)
        except (TypeError, ValueError) as exc:
            raise ValueError("Owner social OAuth token expiry is invalid.") from exc

    return OwnerSocialOAuthTokenResponse(
        access_token=access_token,
        token_type=token_type,
        expires_in=expires_in,
    )


def get_owner_social_profile(provider, access_token):
    if not access_token:
        raise ValueError("Owner social OAuth access token is required.")

    config = get_owner_social_oauth_provider_config(provider)
    prefix = _provider_prefix(provider)
    profile_endpoint = str(
        getattr(settings, f"{prefix}PROFILE_ENDPOINT", "") or ""
    ).strip()
    profile_fields = tuple(
        field.strip()
        for field in str(getattr(settings, f"{prefix}PROFILE_FIELDS", "") or "").split(",")
        if field.strip()
    )
    if not profile_endpoint:
        raise ValueError("Owner social OAuth profile endpoint is not configured.")

    query = {}
    if profile_fields:
        query["fields"] = ",".join(profile_fields)

    profile_url = profile_endpoint
    if query:
        profile_url = f"{profile_endpoint}?{urlencode(query)}"

    request = Request(
        profile_url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise ValueError("Owner social OAuth profile request failed.") from exc

    provider_user_id = str(payload.get("id", "") or "").strip()
    username = str(payload.get("username", "") or "").strip()
    if not provider_user_id:
        raise ValueError("Owner social OAuth profile response is invalid.")

    return OwnerSocialOAuthProfile(
        provider_user_id=provider_user_id,
        username=username,
    )
