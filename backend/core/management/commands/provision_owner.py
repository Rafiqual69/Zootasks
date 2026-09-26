from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction

from accounts.models import AccountEntity


class Command(BaseCommand):
    help = (
        "Provision the single canonical ZooTasks Owner entity for the "
        "pre-existing configured privileged user."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Explicitly confirm Owner provisioning.",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError(
                "Owner provisioning requires explicit --confirm."
            )

        username = getattr(settings, "OWNER_USERNAME", "").strip()
        identity_email = getattr(
            settings, "OWNER_IDENTITY_EMAIL", ""
        ).strip()

        if not username:
            raise CommandError("OWNER_USERNAME is not configured.")

        if not identity_email:
            raise CommandError(
                "OWNER_IDENTITY_EMAIL is not configured."
            )

        try:
            validate_email(identity_email)
        except ValidationError as exc:
            raise CommandError(
                "OWNER_IDENTITY_EMAIL is invalid."
            ) from exc

        User = get_user_model()

        with transaction.atomic():
            try:
                user = (
                    User.objects
                    .select_for_update()
                    .get(username=username)
                )
            except User.DoesNotExist as exc:
                raise CommandError(
                    "Configured Owner user does not exist."
                ) from exc

            if not user.is_active:
                raise CommandError(
                    "Configured Owner user is inactive."
                )

            if not user.is_staff or not user.is_superuser:
                raise CommandError(
                    "Configured Owner user is not sufficiently privileged."
                )

            if AccountEntity.objects.filter(
                entity_type=AccountEntity.EntityType.OWNER
            ).exists():
                raise CommandError(
                    "A canonical Owner entity already exists."
                )

            if AccountEntity.objects.filter(user=user).exists():
                raise CommandError(
                    "Configured Owner user already has an AccountEntity."
                )

            try:
                entity = AccountEntity.objects.create(
                    user=user,
                    entity_type=AccountEntity.EntityType.OWNER,
                    identity_email=identity_email,
                    is_active=True,
                )
            except IntegrityError as exc:
                raise CommandError(
                    "Owner provisioning was rejected by an integrity constraint."
                ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Canonical Owner entity provisioned for username '{entity.user.username}'. "
                "Email remains unverified until the Owner verification flow completes."
            )
        )
