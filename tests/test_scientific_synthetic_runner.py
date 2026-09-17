"""Strict-result tests use fake unittest results; no scientific call or arrays."""

from __future__ import annotations

import io
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import run_scientific_synthetic_contracts as runner


def result(**changes):
    fields = {"testsRun": 5, "skipped": [], "failures": [], "errors": [],
              "expectedFailures": [], "unexpectedSuccesses": []}
    fields.update(changes)
    return SimpleNamespace(**fields)


class ScientificSyntheticRunnerTests(unittest.TestCase):
    def test_exact_five_passes_are_required(self):
        report = runner.evaluate_result(result())
        self.assertEqual(report["status"], "PASS")
        for key, value in runner.EXPECTED_COUNTS.items():
            self.assertEqual(report[key], value)

    def test_skip_is_failure_even_if_unittest_would_succeed(self):
        report = runner.evaluate_result(result(skipped=[("synthetic", "dependency absent")]))
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["passed"], 4)
        self.assertEqual(report["skipped"], 1)

    def test_every_failure_category_blocks(self):
        for field in ("failures", "errors", "expectedFailures", "unexpectedSuccesses"):
            with self.subTest(field=field):
                self.assertEqual(runner.evaluate_result(result(**{field: ["synthetic"]}))["status"], "BLOCKED")

    def test_wrong_test_count_or_noninteger_count_blocks(self):
        for count in (0, 4, 6, True, 5.0):
            with self.subTest(count=count):
                self.assertEqual(runner.evaluate_result(result(testsRun=count))["status"], "BLOCKED")

    def test_versions_come_from_imported_modules(self):
        with patch.object(runner.importlib, "import_module",
                          side_effect=lambda name: SimpleNamespace(__version__=runner.REQUIRED_VERSIONS[name])) as importer:
            self.assertEqual(runner.imported_versions(), {"numpy": "1.26.4", "scipy": "1.11.4"})
        self.assertEqual([call.args[0] for call in importer.call_args_list], ["numpy", "scipy"])

    def test_wrong_or_missing_versions_block_before_loading_suite(self):
        for versions in ({"numpy": "1.26.4", "scipy": "1.11.5"}, {"numpy": "1.26.4"}):
            with patch.object(runner, "imported_versions", return_value=versions), \
                    patch.object(runner, "exact_suite") as loader, \
                    patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(runner.main(), 1)
            loader.assert_not_called()

    def test_import_failure_is_reported_as_nonzero(self):
        with patch.object(runner, "imported_versions", side_effect=ImportError), \
                patch.object(runner, "exact_suite") as loader, \
                patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(runner.main(), 1)
        loader.assert_not_called()

    def test_exact_suite_selection_rejects_different_ids(self):
        fake = [SimpleNamespace(id=lambda: "wrong.test") for _ in range(5)]
        with patch.object(runner.unittest.defaultTestLoader, "loadTestsFromName", return_value=fake) as loader:
            with self.assertRaises(ValueError):
                runner.exact_suite()
        loader.assert_called_once_with("tests.test_ti2_registration.SyntheticImageMatchingTests")

    def test_exact_suite_selection_accepts_only_the_five_frozen_ids(self):
        fake = [SimpleNamespace(id=lambda name=name: f"{runner.TEST_CLASS}.{name}")
                for name in sorted(runner.TEST_NAMES)]
        with patch.object(runner.unittest.defaultTestLoader, "loadTestsFromName", return_value=fake):
            self.assertIs(runner.exact_suite(), fake)

    def test_cli_exit_is_nonzero_for_skip_and_zero_only_for_five_passes(self):
        for fake_result, expected_exit in ((result(), 0), (result(skipped=[("x", "absent")]), 1)):
            with patch.object(runner, "imported_versions", return_value=dict(runner.REQUIRED_VERSIONS)), \
                    patch.object(runner, "exact_suite", return_value="fake suite"), \
                    patch.object(runner.unittest, "TextTestRunner") as factory, \
                    patch("sys.stdout", new_callable=io.StringIO):
                factory.return_value.run.return_value = fake_result
                self.assertEqual(runner.main(), expected_exit)
                factory.return_value.run.assert_called_once_with("fake suite")


if __name__ == "__main__":
    unittest.main()
