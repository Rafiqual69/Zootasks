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


class WorkerDashboardEntityBoundaryTests(TestCase):
    def setUp(self):
        self.worker = get_user_model().objects.create_user(
            username="dashboard-worker",
            password="Strong-Worker-Password-123!",
        )
        WorkerProfile.objects.create(user=self.worker)
        AccountEntity.objects.create(
            user=self.worker,
            entity_type=AccountEntity.EntityType.WORKER,
        )

    def test_active_worker_can_access_dashboard(self):
        self.client.force_login(self.worker)

        response = self.client.get(
            reverse("dashboard"),
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)

    def test_privileged_entity_cannot_access_worker_dashboard(self):
        self.worker.account_entity.entity_type = AccountEntity.EntityType.ADMIN
        self.worker.account_entity.save(update_fields=["entity_type"])

        self.client.force_login(self.worker)

        response = self.client.get(
            reverse("dashboard"),
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            WorkerProfile.objects.filter(user=self.worker).exists()
        )

    def test_user_without_entity_cannot_access_or_create_worker_profile(self):
        user = get_user_model().objects.create_user(
            username="dashboard-no-entity",
            password="Strong-Worker-Password-123!",
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard"),
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            WorkerProfile.objects.filter(user=user).exists()
        )

    def test_inactive_worker_cannot_access_dashboard(self):
        self.worker.account_entity.is_active = False
        self.worker.account_entity.save(update_fields=["is_active"])

        self.client.force_login(self.worker)

        response = self.client.get(
            reverse("dashboard"),
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 403)
