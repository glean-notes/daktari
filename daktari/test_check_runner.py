import unittest
from io import StringIO
from unittest.mock import patch

from colors import red, yellow, green

from daktari.check_runner import run_checks
from daktari.test_check_factory import DummyCheck, ExplodingCheck


class TestCheckRunner(unittest.TestCase):
    def test_status_all_passing(self):
        checks = [DummyCheck("check.one", succeed=True), DummyCheck("check.two", succeed=True)]
        result = run_checks(checks, quiet_mode=True, fail_fast=False)
        self.assertTrue(result)

    def test_runs_all_and_returns_failure_if_check_fails(self):
        final_check = DummyCheck("check.three", succeed=True)
        checks = [DummyCheck("check.one", succeed=True), DummyCheck("check.two", succeed=False), final_check]
        result = run_checks(checks, quiet_mode=True, fail_fast=False)
        self.assertFalse(result)
        self.assertTrue(final_check.was_run)

    def test_aborts_and_returns_failure_if_check_fails_and_fail_fast(self):
        final_check = DummyCheck("check.three", succeed=True)
        checks = [DummyCheck("check.one", succeed=True), DummyCheck("check.two", succeed=False), final_check]
        result = run_checks(checks, quiet_mode=True, fail_fast=True)
        self.assertFalse(result)
        self.assertFalse(final_check.was_run)

    def test_copes_with_unhandled_errors_and_runs_later_checks(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            final_check = DummyCheck("check.three", succeed=True)
            checks = [ExplodingCheck(), final_check]
            result = run_checks(checks, quiet_mode=True, fail_fast=False)
            self.assertFalse(result)
            self.assertTrue(final_check.was_run)
            self.assertIn(f"💥 [{red('exploding.check')}] Check failed with unhandled Exception", fake_out.getvalue())

    def test_skips_dependents_on_failure(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            final_check = DummyCheck("dependent.check", depends_on=[ExplodingCheck], succeed=True)
            checks = [ExplodingCheck(), final_check]
            result = run_checks(checks, quiet_mode=True, fail_fast=False)
            self.assertFalse(result)
            self.assertFalse(final_check.was_run)
            self.assertIn(f"⚠️  [{yellow('dependent.check')}] skipped due to previous failures", fake_out.getvalue())

    def test_skips_missing_dependencies(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            missing_check = DummyCheck("check.one")
            final_check = DummyCheck("dependent.check", depends_on=[missing_check])
            checks = [final_check]
            result = run_checks(checks, quiet_mode=True, fail_fast=False)
            self.assertTrue(result)
            self.assertFalse(final_check.was_run)
            self.assertIn(
                f"⚠️  [{yellow('dependent.check')}] skipped due to missing dependent checks: check.one",
                fake_out.getvalue(),
            )

    def test_outputs_success(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            checks = [DummyCheck("check.one", succeed=True)]
            result = run_checks(checks, quiet_mode=False, fail_fast=False)
            self.assertTrue(result)
            self.assertIn(f"✅ [{green('check.one')}] dummy check", fake_out.getvalue())

    def test_suppresses_success_in_quiet_mode(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            checks = [DummyCheck("check.one", succeed=True)]
            result = run_checks(checks, quiet_mode=True, fail_fast=False)
            self.assertTrue(result)
            self.assertNotIn("✅", fake_out.getvalue())

    def test_outputs_failure_in_quiet_mode(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            checks = [DummyCheck("check.one", succeed=False)]
            result = run_checks(checks, quiet_mode=True, fail_fast=False)
            self.assertFalse(result)
            self.assertIn(f"❌ [{red('check.one')}] dummy check", fake_out.getvalue())
