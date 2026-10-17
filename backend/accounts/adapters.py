from django.db import transaction
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import AccountEntity, WorkerProfile


class SafeGoogleSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Allow Google sign-in only and provision new users as ordinary workers."""

    def is_open_for_signup(self, request, sociallogin):
        return sociallogin.account.provider == "google"

    def save_user(self, request, sociallogin, form=None):
        # Never grant Owner/admin status through a third-party identity provider.
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
