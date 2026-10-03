import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from django.conf import settings

from .models import OwnerSocialIdentity
from .social_oauth_provider import get_owner_social_oauth_provider_config


MAX_OAUTH_RESPONSE_BYTES = 64 * 1024


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Owner social OAuth redirects are not allowed.")


_NO_REDIRECT_OPENER = build_opener(_NoRedirectHandler)


def urlopen(request, timeout=10):
    return _NO_REDIRECT_OPENER.open(request, timeout=timeout)


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
            status = getattr(response, "status", None)
            if isinstance(status, int) and not 200 <= status < 300:
                raise ValueError("Owner social OAuth token exchange failed.")
            raw_body = response.read(MAX_OAUTH_RESPONSE_BYTES + 1)
            if len(raw_body) > MAX_OAUTH_RESPONSE_BYTES:
                raise ValueError("Owner social OAuth response is too large.")
            payload = json.loads(raw_body.decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Owner social OAuth token exchange failed.") from None

    if not isinstance(payload, dict):
        raise ValueError("Owner social OAuth token response is invalid.")

    access_token = str(payload.get("access_token", "") or "").strip()
    if not access_token:
        raise ValueError("Owner social OAuth token response is invalid.")

    token_type = str(payload.get("token_type", "Bearer") or "Bearer").strip()
    if token_type.lower() != "bearer":
        raise ValueError("Owner social OAuth token response is invalid.")

    expires_in = payload.get("expires_in")
    if expires_in is not None:
        if isinstance(expires_in, bool):
            raise ValueError("Owner social OAuth token expiry is invalid.")
        try:
            expires_in = int(expires_in)
        except (TypeError, ValueError) as exc:
            raise ValueError("Owner social OAuth token expiry is invalid.") from exc
        if expires_in < 0:
            raise ValueError("Owner social OAuth token expiry is invalid.")

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
    parsed_profile_endpoint = urlparse(profile_endpoint)
    if (
        parsed_profile_endpoint.scheme != "https"
        or parsed_profile_endpoint.username
        or parsed_profile_endpoint.password
        or (parsed_profile_endpoint.hostname or "").lower() not in {
            "facebook.com",
            "www.facebook.com",
            "graph.facebook.com",
            "instagram.com",
            "www.instagram.com",
            "api.instagram.com",
            "graph.instagram.com",
        }
    ):
        raise ValueError("Owner social OAuth profile endpoint uses an unapproved host.")

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
            status = getattr(response, "status", None)
            if isinstance(status, int) and not 200 <= status < 300:
                raise ValueError("Owner social OAuth profile request failed.")
            raw_body = response.read(MAX_OAUTH_RESPONSE_BYTES + 1)
            if len(raw_body) > MAX_OAUTH_RESPONSE_BYTES:
                raise ValueError("Owner social OAuth response is too large.")
            payload = json.loads(raw_body.decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Owner social OAuth profile request failed.") from None

    if not isinstance(payload, dict):
        raise ValueError("Owner social OAuth profile response is invalid.")

    provider_user_id = str(payload.get("id", "") or "").strip()
    username = str(payload.get("username", "") or "").strip()
    if not provider_user_id:
        raise ValueError("Owner social OAuth profile response is invalid.")

    return OwnerSocialOAuthProfile(
        provider_user_id=provider_user_id,
        username=username,
    )
