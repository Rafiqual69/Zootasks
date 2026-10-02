from django.test import SimpleTestCase

from .ai_data_boundary import (
    AIDataBoundaryError,
    build_task_content_projection,
)


class AIDataBoundaryTests(SimpleTestCase):
    def test_projection_is_explicitly_allowlisted(self):
        result = build_task_content_projection(
            title="Test",
            description="Do the task",
            category="Testing",
        )
        self.assertEqual(set(result), {"title", "description", "category"})

    def test_unknown_data_class_fails_closed(self):
        with self.assertRaisesMessage(AIDataBoundaryError, "ai_data_class_not_allowed"):
            build_task_content_projection(
                title="Test",
                description="Do the task",
                category="Testing",
                data_class="wallet_financial",
            )

    def test_credentials_are_redacted(self):
        result = build_task_content_projection(
            title="Test",
            description="Use api_key=SECRET123 and Bearer abcdefgh123456",
            category="Testing",
        )
        self.assertNotIn("SECRET123", result["description"])
        self.assertNotIn("abcdefgh123456", result["description"])
        self.assertIn("[REDACTED:CREDENTIAL]", result["description"])
        self.assertIn("[REDACTED:BEARER]", result["description"])

    def test_personal_contact_data_is_redacted(self):
        result = build_task_content_projection(
            title="Contact",
            description="Email worker@example.com or call +880 1712 345678",
            category="Testing",
        )
        self.assertNotIn("worker@example.com", result["description"])
        self.assertNotIn("1712 345678", result["description"])

    def test_required_task_content_is_checked_before_provider_boundary(self):
        with self.assertRaisesMessage(AIDataBoundaryError, "ai_task_content_required"):
            build_task_content_projection(title="", description="x", category="Testing")
