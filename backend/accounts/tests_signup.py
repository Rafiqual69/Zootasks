from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AccountEntity, AdvertiserProfile, WorkerProfile


class WorkerSignupEntityTests(TestCase):
    def test_registration_creates_worker_entity_and_profile(self):
        response = self.client.post(reverse("register"), {
            "username": "new-worker", "email": "worker@example.com",
            "first_name": "New", "last_name": "Worker",
            "password": "Strong-Worker-Password-123!",
            "password_confirm": "Strong-Worker-Password-123!",
        }, HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="new-worker")
        entity = AccountEntity.objects.get(user=user)
        self.assertEqual(entity.entity_type, AccountEntity.EntityType.WORKER)
        self.assertEqual(entity.identity_email, "worker@example.com")
        self.assertIsNone(entity.email_verified_at)
        self.assertTrue(WorkerProfile.objects.filter(user=user).exists())
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_worker_signup_never_creates_privileged_entity(self):
        self.client.post(reverse("register"), {
            "username": "another-worker", "email": "another@example.com",
            "first_name": "Another", "last_name": "Worker",
            "password": "Strong-Worker-Password-123!",
            "password_confirm": "Strong-Worker-Password-123!",
        }, HTTP_HOST="127.0.0.1")
        user = get_user_model().objects.get(username="another-worker")
        entity = AccountEntity.objects.get(user=user)
        self.assertEqual(entity.entity_type, AccountEntity.EntityType.WORKER)
        self.assertFalse(AccountEntity.objects.filter(
            user=user,
            entity_type__in=[
                AccountEntity.EntityType.OWNER, AccountEntity.EntityType.SUPER_ADMIN,
                AccountEntity.EntityType.ADMIN, AccountEntity.EntityType.ADVERTISER,
            ],
        ).exists())


class WorkerDashboardEntityBoundaryTests(TestCase):
    def setUp(self):
        self.worker = get_user_model().objects.create_user(
            username="dashboard-worker", password="Strong-Worker-Password-123!"
        )
        WorkerProfile.objects.create(user=self.worker)
        AccountEntity.objects.create(user=self.worker, entity_type=AccountEntity.EntityType.WORKER)

    def test_active_worker_can_access_dashboard(self):
        self.client.force_login(self.worker)
        response = self.client.get(reverse("dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 200)

    def test_privileged_entity_cannot_access_worker_dashboard(self):
        self.worker.account_entity.entity_type = AccountEntity.EntityType.ADMIN
        self.worker.account_entity.save(update_fields=["entity_type"])
        self.client.force_login(self.worker)
        response = self.client.get(reverse("dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(WorkerProfile.objects.filter(user=self.worker).exists())

    def test_user_without_entity_cannot_access_or_create_worker_profile(self):
        user = get_user_model().objects.create_user(
            username="dashboard-no-entity", password="Strong-Worker-Password-123!"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(WorkerProfile.objects.filter(user=user).exists())

    def test_inactive_worker_cannot_access_dashboard(self):
        self.worker.account_entity.is_active = False
        self.worker.account_entity.save(update_fields=["is_active"])
        self.client.force_login(self.worker)
        response = self.client.get(reverse("dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 403)


class AdvertiserSignupEntityTests(TestCase):
    def test_advertiser_signup_creates_only_advertiser_entity_and_profile(self):
        response = self.client.post(reverse("advertiser_register"), {
            "username": "new-advertiser", "email": "advertiser@example.com",
            "first_name": "Contact", "last_name": "Person",
            "organization_name": "Zoo Business", "contact_name": "Contact Person",
            "password": "Strong-Advertiser-Password-123!",
            "password_confirm": "Strong-Advertiser-Password-123!",
        }, HTTP_HOST="127.0.0.1")
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        user = get_user_model().objects.get(username="new-advertiser")
        entity = AccountEntity.objects.get(user=user)
        self.assertEqual(entity.entity_type, AccountEntity.EntityType.ADVERTISER)
        self.assertEqual(entity.identity_email, "advertiser@example.com")
        self.assertFalse(WorkerProfile.objects.filter(user=user).exists())
        profile = AdvertiserProfile.objects.get(user=user)
        self.assertEqual(profile.organization_name, "Zoo Business")
        self.assertEqual(profile.contact_name, "Contact Person")
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_advertiser_signup_rejects_duplicate_email(self):
        User = get_user_model()
        User.objects.create_user(username="existing-email", email="advertiser@example.com")
        response = self.client.post(reverse("advertiser_register"), {
            "username": "another-advertiser", "email": "ADVERTISER@example.com",
            "first_name": "Contact", "last_name": "Person",
            "organization_name": "Zoo Business", "contact_name": "Contact Person",
            "password": "Strong-Advertiser-Password-123!",
            "password_confirm": "Strong-Advertiser-Password-123!",
        }, HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email is already registered.")
        self.assertFalse(AccountEntity.objects.filter(identity_email__iexact="advertiser@example.com").exists())

    def test_advertiser_cannot_access_worker_dashboard(self):
        user = get_user_model().objects.create_user(
            username="advertiser-boundary", password="Strong-Advertiser-Password-123!"
        )
        AccountEntity.objects.create(
            user=user, entity_type=AccountEntity.EntityType.ADVERTISER,
            identity_email="boundary@example.com",
        )
        AdvertiserProfile.objects.create(user=user, organization_name="Boundary Co")
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 403)

    def test_only_advertiser_can_access_advertiser_dashboard(self):
        user = get_user_model().objects.create_user(
            username="advertiser-dashboard", password="Strong-Advertiser-Password-123!"
        )
        AccountEntity.objects.create(
            user=user, entity_type=AccountEntity.EntityType.ADVERTISER,
        )
        AdvertiserProfile.objects.create(user=user, organization_name="Dashboard Co")
        self.client.force_login(user)
        response = self.client.get(reverse("advertiser_dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 200)

    def test_worker_cannot_access_advertiser_dashboard(self):
        self.client.force_login(get_user_model().objects.create_user(
            username="worker-dashboard-boundary", password="Strong-Worker-Password-123!"
        ))
        response = self.client.get(reverse("advertiser_dashboard"), HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 403)

