from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal

from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from .models import Task, TaskClaim


class TaskMarketplaceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="worker1",
            password="StrongTestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="worker2",
            password="StrongTestPass123!",
        )
        AccountEntity.objects.create(
            user=self.user,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        AccountEntity.objects.create(
            user=self.other_user,
            entity_type=AccountEntity.EntityType.WORKER,
        )

        self.active_task = Task.objects.create(
            title="Test Active Task",
            description="Complete this test task.",
            category="Testing",
            reward="10.00",
            max_workers=2,
        )

        self.paused_task = Task.objects.create(
            title="Paused Task",
            description="This task must not appear.",
            category="Testing",
            reward="20.00",
            max_workers=1,
            status="paused",
        )

    def login(self):
        self.client.force_login(self.user)

    def test_marketplace_requires_login(self):
        response = self.client.get(reverse("task_marketplace"))
        self.assertEqual(response.status_code, 302)

    def test_non_worker_is_denied(self):
        owner = User.objects.create_user(
            username="task-owner",
            password="StrongTestPass123!",
        )
        AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.client.force_login(owner)

        response = self.client.get(reverse("task_marketplace"))

        self.assertEqual(response.status_code, 403)

    def test_marketplace_shows_active_tasks(self):
        self.login()

        response = self.client.get(reverse("task_marketplace"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Active Task")
        self.assertNotContains(response, "Paused Task")

    def test_get_claim_does_not_claim_task(self):
        self.login()

        response = self.client.get(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).count(),
            0,
        )
        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 0)

    def test_worker_can_claim_active_task(self):
        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        self.assertTrue(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
                status="claimed",
            ).exists()
        )

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 1)
        self.assertEqual(self.active_task.status, "active")

    def test_worker_cannot_claim_same_task_twice(self):
        self.login()

        self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )
        self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertEqual(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).count(),
            1,
        )

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 1)

    def test_full_task_cannot_be_claimed(self):
        self.active_task.max_workers = 1
        self.active_task.reserved_workers = 1
        self.active_task.completed_workers = 1
        self.active_task.status = "active"
        self.active_task.save(
            update_fields=[
                "max_workers",
                "reserved_workers",
                "completed_workers",
                "status",
            ]
        )

        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))
        self.assertFalse(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).exists()
        )

    def test_last_available_slot_completes_task(self):
        self.active_task.max_workers = 1
        self.active_task.save(update_fields=["max_workers"])

        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 1)
        self.assertEqual(self.active_task.status, "completed")

    def test_submit_requires_existing_claim(self):
        self.login()

        response = self.client.get(
            reverse("submit_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_claimed_worker_can_submit_proof(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )

        self.login()

        response = self.client.post(
            reverse("submit_task", args=[self.active_task.id]),
            {"proof": "Completed the task successfully."},
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        claim.refresh_from_db()
        self.assertEqual(claim.status, "submitted")
        self.assertEqual(
            claim.proof,
            "Completed the task successfully.",
        )
        self.assertIsNotNone(claim.submitted_at)

    def test_submit_page_escapes_task_content(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )
        self.active_task.title = "<script>alert('x')</script>"
        self.active_task.description = "<img src=x onerror=alert('x')>"
        self.active_task.save(update_fields=["title", "description"])

        self.login()

        response = self.client.get(
            reverse("submit_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;", html=False)
        self.assertContains(response, "&lt;img src=x onerror=alert(&#x27;x&#x27;)&gt;", html=False)

    def test_empty_proof_does_not_submit(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )

        self.login()

        response = self.client.post(
            reverse("submit_task", args=[self.active_task.id]),
            {"proof": "   "},
        )

        self.assertEqual(response.status_code, 200)

        claim.refresh_from_db()
        self.assertEqual(claim.status, "claimed")
        self.assertEqual(claim.proof, "")
        self.assertIsNone(claim.submitted_at)


class AdminWriteBoundaryTests(TestCase):
    def test_task_protected_fields_are_read_only(self):
        from django.contrib import admin
        from tasks.admin import TaskAdmin

        model_admin = TaskAdmin(Task, admin.site)
        self.assertEqual(
            set(model_admin.readonly_fields),
            {
                "reward",
                "max_workers",
                "reserved_workers",
                "completed_workers",
                "status",
            },
        )


class AdminReadBoundaryTests(TestCase):
    def test_task_claim_admin_does_not_search_submission_proof(self):
        from django.contrib import admin
        from tasks.admin import TaskClaimAdmin

        model_admin = TaskClaimAdmin(TaskClaim, admin.site)
        self.assertNotIn("proof", model_admin.search_fields)
        self.assertIn("task__title", model_admin.search_fields)
        self.assertIn("worker__username", model_admin.search_fields)


class TaskClaimAdminReadBoundaryTests(TestCase):
    def test_unprivileged_staff_cannot_view_task_claim_admin(self):
        from django.contrib import admin
        from django.test import RequestFactory
        from tasks.admin import TaskClaimAdmin

        staff = User.objects.create_user(
            username="limited_task_staff",
            password="test-password-123",
            is_staff=True,
        )
        model_admin = TaskClaimAdmin(TaskClaim, admin.site)
        request = RequestFactory().get("/admin/tasks/taskclaim/")
        request.user = staff

        self.assertFalse(model_admin.has_view_permission(request))

    def test_task_reviewer_can_view_task_claim_admin(self):
        from django.contrib import admin
        from django.contrib.auth.models import Permission
        from django.test import RequestFactory
        from tasks.admin import TaskClaimAdmin

        reviewer = User.objects.create_user(
            username="task_reviewer",
            password="test-password-123",
            is_staff=True,
        )
        reviewer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="tasks",
                codename="approve_task_submission",
            )
        )
        model_admin = TaskClaimAdmin(TaskClaim, admin.site)
        request = RequestFactory().get("/admin/tasks/taskclaim/")
        request.user = reviewer

        self.assertTrue(model_admin.has_view_permission(request))


class TaskRewardOperationIntegrityTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(username="task_reward_worker", password="test-password-123")
        AccountEntity.objects.create(user=self.worker, entity_type=AccountEntity.EntityType.WORKER)
        WorkerProfile.objects.create(
            user=self.worker,
            balance=Decimal("100.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("100.00"),
        )
        self.task = Task.objects.create(
            title="Integrity Task",
            description="Test",
            category="Testing",
            reward=Decimal("25.00"),
            max_workers=1,
        )
        self.claim = TaskClaim.objects.create(task=self.task, worker=self.worker, status="submitted")

        class ModelAdminStub:
            def message_user(self, request, message, level=None):
                pass
        self.modeladmin = ModelAdminStub()
        self.request = type("RequestStub", (), {})()
        self.request.user = User.objects.create_superuser(username="task_integrity_admin", password="test-admin-password")

    def test_mismatched_existing_payment_does_not_approve_claim(self):
        WalletTransaction.objects.create(
            user=self.worker,
            amount=Decimal("20.00"),
            transaction_type="earning",
            description="Integrity mismatch",
            task_claim=self.claim,
        )

        from tasks.admin import approve_submissions
        approve_submissions(self.modeladmin, self.request, TaskClaim.objects.filter(pk=self.claim.pk))

        self.claim.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.worker)
        self.assertEqual(self.claim.status, "submitted")
        self.assertEqual(profile.balance, Decimal("100.00"))
        self.assertEqual(profile.total_earned, Decimal("100.00"))


class FinancialAdminHttpTamperingTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="http_task_owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.task = Task.objects.create(
            title="Protected Task",
            description="Protected task",
            category="Testing",
            reward="25.00",
            max_workers=5,
            reserved_workers=1,
            completed_workers=1,
            status="active",
        )
        self.client.force_login(self.owner)

    def test_change_post_cannot_tamper_protected_fields(self):
        url = reverse("admin:tasks_task_change", args=[self.task.pk])
        response = self.client.post(
            url,
            {
                "title": "Updated Title",
                "description": "Updated description",
                "category": "Testing",
                "reward": "9999.99",
                "max_workers": "999",
                "completed_workers": "999",
                "status": "completed",
                "deadline": "",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Title")
        self.assertEqual(self.task.description, "Updated description")
        self.assertEqual(self.task.reward, Decimal("25.00"))
        self.assertEqual(self.task.max_workers, 5)
        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(self.task.status, "active")

    def test_owner_can_create_task_with_financial_fields(self):
        url = reverse("admin:tasks_task_add")
        response = self.client.post(
            url,
            {
                "title": "Owner Created Task",
                "description": "Created through authorized admin flow",
                "category": "Testing",
                "reward": "35.00",
                "max_workers": "3",
                "completed_workers": "0",
                "status": "active",
                "deadline": "",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title="Owner Created Task")
        self.assertEqual(task.reward, Decimal("35.00"))
        self.assertEqual(task.max_workers, 3)
        self.assertEqual(task.completed_workers, 0)
        self.assertEqual(task.status, "active")

    def test_non_owner_cannot_create_task(self):
        non_owner = User.objects.create_user(
            username="http_task_add_non_owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(non_owner)

        url = reverse("admin:tasks_task_add")
        response = self.client.post(
            url,
            {
                "title": "Unauthorized Created Task",
                "description": "Must not be created",
                "category": "Testing",
                "reward": "9999.99",
                "max_workers": "999",
                "completed_workers": "999",
                "status": "active",
                "deadline": "",
                "_save": "Save",
            },
        )

        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(
            Task.objects.filter(title="Unauthorized Created Task").exists()
        )


    def test_non_owner_cannot_post_task_change(self):
        non_owner = User.objects.create_user(
            username="http_task_non_owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(non_owner)

        url = reverse("admin:tasks_task_change", args=[self.task.pk])
        response = self.client.post(
            url,
            {
                "title": "Unauthorized Change",
                "description": "Unauthorized",
                "category": "Testing",
                "reward": "9999.99",
                "max_workers": "999",
                "completed_workers": "999",
                "status": "completed",
                "deadline": "",
                "_save": "Save",
            },
        )

        self.assertIn(response.status_code, (302, 403))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Protected Task")
        self.assertEqual(self.task.reward, Decimal("25.00"))
        self.assertEqual(self.task.max_workers, 5)
        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(self.task.status, "active")


class FinancialAdminPolicyBoundaryTests(TestCase):
    def setUp(self):
        from django.contrib import admin
        from tasks.admin import TaskAdmin

        self.owner = User.objects.create_user(
            username="policy_task_owner", password="test-password-123",
            is_staff=True, is_superuser=True,
        )
        AccountEntity.objects.create(
            user=self.owner, entity_type=AccountEntity.EntityType.OWNER,
        )
        self.non_owner = User.objects.create_user(
            username="policy_task_non_owner", password="test-password-123",
            is_staff=True, is_superuser=True,
        )
        self.admin = TaskAdmin(Task, admin.site)

    def request_for(self, user):
        return type("Request", (), {"user": user})()

    def test_owner_policy_allows_create_and_change(self):
        request = self.request_for(self.owner)
        self.assertTrue(self.admin.has_add_permission(request))
        task = Task(
            title="Existing", description="Existing task",
            reward="10.00", max_workers=2,
        )
        self.assertTrue(self.admin.has_change_permission(request, task))

    def test_non_owner_is_denied_by_policy(self):
        request = self.request_for(self.non_owner)
        self.assertFalse(self.admin.has_add_permission(request))
        task = Task(
            title="Existing", description="Existing task",
            reward="10.00", max_workers=2,
        )
        self.assertFalse(self.admin.has_change_permission(request, task))

    def test_inactive_owner_entity_is_denied_by_policy(self):
        request = self.request_for(self.owner)
        entity = AccountEntity.objects.get(user=self.owner)
        entity.is_active = False
        entity.save(update_fields=["is_active"])

        task = Task(
            title="Existing",
            description="Existing task",
            reward="10.00",
            max_workers=2,
        )

        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request, task))


    def test_protected_fields_are_immutable_on_existing_objects(self):
        request = self.request_for(self.owner)
        task = Task(
            title="Existing", description="Existing task",
            reward="10.00", max_workers=2,
        )
        self.assertEqual(
            set(self.admin.get_readonly_fields(request, task)),
            {"reward", "max_workers", "completed_workers", "status"},
        )
