from dataclasses import dataclass
from urllib.parse import urlencode, urlparse

from django.conf import settings

from .models import OwnerSocialIdentity


@dataclass(frozen=True)
class OwnerSocialOAuthProviderConfig:
    provider: str
    client_id: str
    authorization_endpoint: str
    token_endpoint: str
    redirect_uri: str
    scopes: tuple[str, ...]


_PROVIDER_OAUTH_HOSTS = {
    OwnerSocialIdentity.Provider.FACEBOOK: {
        "facebook.com",
        "www.facebook.com",
        "graph.facebook.com",
    },
    OwnerSocialIdentity.Provider.INSTAGRAM: {
        "instagram.com",
        "www.instagram.com",
        "api.instagram.com",
        "graph.instagram.com",
    },
}


def _validate_provider_endpoint(value, setting_name, provider):
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise ValueError(f"{setting_name} must use HTTPS without embedded credentials.")
    hostname = (parsed.hostname or "").lower()
    if hostname not in _PROVIDER_OAUTH_HOSTS[provider]:
        raise ValueError(f"{setting_name} uses an unapproved OAuth host.")
    return value


def _validate_redirect_uri(value, setting_name):
    parsed = urlparse(value)
    if (
        parsed.scheme not in {"https", "http"}
        or parsed.username
        or parsed.password
        or parsed.fragment
        or not parsed.hostname
    ):
        raise ValueError(
            f"{setting_name} must be an absolute HTTPS redirect URI without "
            "embedded credentials or fragments."
        )
    if parsed.scheme == "http":
        hostname = (parsed.hostname or "").lower()
        if getattr(settings, "PRODUCTION_MODE", False) or hostname not in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            raise ValueError(
                f"{setting_name} must use HTTPS outside localhost development."
            )
    return value


def get_owner_social_oauth_provider_config(provider):
    if provider == OwnerSocialIdentity.Provider.FACEBOOK:
        prefix = "OWNER_FACEBOOK_OAUTH_"
    elif provider == OwnerSocialIdentity.Provider.INSTAGRAM:
        prefix = "OWNER_INSTAGRAM_OAUTH_"
    else:
        raise ValueError("Unsupported Owner social provider.")

    client_id = str(getattr(settings, f"{prefix}CLIENT_ID", "") or "").strip()
    authorization_endpoint = str(
        getattr(settings, f"{prefix}AUTHORIZATION_ENDPOINT", "") or ""
    ).strip()
    token_endpoint = str(getattr(settings, f"{prefix}TOKEN_ENDPOINT", "") or "").strip()
    redirect_uri = str(getattr(settings, f"{prefix}REDIRECT_URI", "") or "").strip()
    scopes = tuple(
        scope.strip()
        for scope in str(getattr(settings, f"{prefix}SCOPES", "") or "").split(",")
        if scope.strip()
    )

    if not client_id:
        raise ValueError("Owner social OAuth client ID is not configured.")
    if not authorization_endpoint:
        raise ValueError("Owner social OAuth authorization endpoint is not configured.")
    if not token_endpoint:
        raise ValueError("Owner social OAuth token endpoint is not configured.")
    authorization_endpoint = _validate_provider_endpoint(
        authorization_endpoint, f"{prefix}AUTHORIZATION_ENDPOINT", provider
    )
    token_endpoint = _validate_provider_endpoint(
        token_endpoint, f"{prefix}TOKEN_ENDPOINT", provider
    )
    if not redirect_uri:
        raise ValueError("Owner social OAuth redirect URI is not configured.")
    redirect_uri = _validate_redirect_uri(
        redirect_uri, f"{prefix}REDIRECT_URI"
    )
    if not scopes:
        raise ValueError("Owner social OAuth scopes are not configured.")

    return OwnerSocialOAuthProviderConfig(
        provider=provider,
        client_id=client_id,
        authorization_endpoint=authorization_endpoint,
        token_endpoint=token_endpoint,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )


def build_owner_social_authorization_url(provider, state):
    if not state:
        raise ValueError("OAuth state is required.")

    config = get_owner_social_oauth_provider_config(provider)
    return f"{config.authorization_endpoint}?{urlencode({
        'client_id': config.client_id,
        'redirect_uri': config.redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(config.scopes),
        'state': state,
    })}"
