from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AccountEntity, WorkerProfile


class WorkerSignupEntityTests(TestCase):
    def test_registration_creates_worker_entity_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-worker",
                "email": "worker@example.com",
                "first_name": "New",
                "last_name": "Worker",
                "password": "Strong-Worker-Password-123!",
                "password_confirm": "Strong-Worker-Password-123!",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="new-worker")
        entity = AccountEntity.objects.get(user=user)

        self.assertEqual(
            entity.entity_type,
            AccountEntity.EntityType.WORKER,
        )
        self.assertEqual(entity.identity_email, "worker@example.com")
        self.assertIsNone(entity.email_verified_at)
        self.assertTrue(WorkerProfile.objects.filter(user=user).exists())
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(user.pk),
        )

    def test_worker_signup_never_creates_privileged_entity(self):
        self.client.post(
            reverse("register"),
            {
                "username": "another-worker",
                "email": "another@example.com",
                "first_name": "Another",
                "last_name": "Worker",
                "password": "Strong-Worker-Password-123!",
                "password_confirm": "Strong-Worker-Password-123!",
            },
            HTTP_HOST="127.0.0.1",
        )

        user = get_user_model().objects.get(username="another-worker")
        entity = AccountEntity.objects.get(user=user)

        self.assertEqual(
            entity.entity_type,
            AccountEntity.EntityType.WORKER,
        )
        self.assertFalse(
            AccountEntity.objects.filter(
                user=user,
                entity_type__in=[
                    AccountEntity.EntityType.OWNER,
                    AccountEntity.EntityType.SUPER_ADMIN,
                    AccountEntity.EntityType.ADMIN,
                    AccountEntity.EntityType.ADVERTISER,
                ],
            ).exists()
        )
