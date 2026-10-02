from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model

from accounts.models import AccountEntity
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = "Promote an existing user to the canonical ZooTasks Owner entity."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Explicitly confirm the security-sensitive Owner promotion.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"].strip()
        if not username:
            raise CommandError("username_required")
        if not options["confirm"]:
            raise CommandError(
                "owner_promotion_requires_explicit_confirmation: use --confirm"
            )

        User = get_user_model()
        try:
            user = User.objects.select_for_update().get(username__iexact=username)
        except User.DoesNotExist as exc:
            raise CommandError("owner_user_not_found") from exc

        if not user.is_active:
            raise CommandError("owner_user_inactive")
        if not user.is_staff or not user.is_superuser:
            raise CommandError("owner_requires_staff_and_superuser")

        if not TOTPDevice.objects.filter(user=user, confirmed=True).exists():
            raise CommandError("owner_requires_confirmed_totp")

        owner_qs = AccountEntity.objects.select_for_update().filter(
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )
        existing_owner = owner_qs.first()

        if existing_owner and existing_owner.user_id != user.id:
            raise CommandError("active_owner_already_exists")

        entity, created = AccountEntity.objects.select_for_update().get_or_create(
            user=user,
            defaults={
                "entity_type": AccountEntity.EntityType.OWNER,
                "identity_email": user.email or None,
                "is_active": True,
            },
        )

        if entity.entity_type != AccountEntity.EntityType.OWNER:
            entity.entity_type = AccountEntity.EntityType.OWNER
            entity.identity_email = user.email or entity.identity_email
            entity.is_active = True
            entity.save(update_fields=[
                "entity_type",
                "identity_email",
                "is_active",
                "updated_at",
            ])
        elif not entity.is_active:
            entity.is_active = True
            entity.save(update_fields=["is_active", "updated_at"])

        self.stdout.write(self.style.SUCCESS(
            f"OWNER_READY username={user.username} entity_id={entity.pk} "
            f"created={created} staff={user.is_staff} superuser={user.is_superuser} "
            f"totp=confirmed"
        ))
