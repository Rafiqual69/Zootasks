from dataclasses import dataclass
from urllib.parse import urlencode

from django.conf import settings

from .models import OwnerSocialIdentity


@dataclass(frozen=True)
class OwnerSocialOAuthProviderConfig:
    provider: str
    client_id: str
    authorization_endpoint: str
    redirect_uri: str
    scopes: tuple[str, ...]


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
    if not redirect_uri:
        raise ValueError("Owner social OAuth redirect URI is not configured.")
    if not scopes:
        raise ValueError("Owner social OAuth scopes are not configured.")

    return OwnerSocialOAuthProviderConfig(
        provider=provider,
        client_id=client_id,
        authorization_endpoint=authorization_endpoint,
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
