from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponseForbidden

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import AccountEntity, WorkerProfile


ALLOWED_SOCIAL_PROVIDERS = {"google", "facebook", "linkedin", "yahoo", "openid_connect"}


class SafeSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Provision ordinary worker accounts; never grant or authenticate Owner access."""

    def is_open_for_signup(self, request, sociallogin):
        return sociallogin.account.provider in ALLOWED_SOCIAL_PROVIDERS

    def pre_social_login(self, request, sociallogin):
        privileged_user = None

        if request.user.is_authenticated:
            privileged_user = request.user
        elif getattr(sociallogin.user, "pk", None):
            privileged_user = get_user_model().objects.filter(
                pk=sociallogin.user.pk
            ).first()

        if privileged_user is not None:
            is_owner = AccountEntity.objects.filter(
                user=privileged_user,
                entity_type=AccountEntity.EntityType.OWNER,
                is_active=True,
            ).exists()
            if privileged_user.is_staff or privileged_user.is_superuser or is_owner:
                raise ImmediateHttpResponse(
                    HttpResponseForbidden(
                        "Social sign-in is unavailable for privileged accounts."
                    )
                )

    def save_user(self, request, sociallogin, form=None):
        with transaction.atomic():
            user = super().save_user(request, sociallogin, form)
            WorkerProfile.objects.get_or_create(user=user)
            AccountEntity.objects.get_or_create(
                user=user,
                defaults={
                    "entity_type": AccountEntity.EntityType.WORKER,
                    "is_active": True,
                },
            )
        return user
