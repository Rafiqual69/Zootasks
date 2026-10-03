from django.test import SimpleTestCase

from core.ai_adversarial_regression import CASES, evaluate_case, run_adversarial_regression


class AIAdversarialRegressionTests(SimpleTestCase):
    def test_all_regression_vectors_match_expected_decisions(self):
        for case in CASES:
            self.assertEqual(
                evaluate_case(case),
                case.expected,
                msg=case.case_id,
            )

    def test_regression_memory_is_stable_and_passes(self):
        passed, digest = run_adversarial_regression()
        self.assertTrue(passed)
        self.assertEqual(len(digest), 64)
