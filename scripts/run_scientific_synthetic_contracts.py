"""Strict CI runner for the five frozen, memory-only synthetic matching tests."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys
import unittest


TEST_CLASS = "tests.test_ti2_registration.SyntheticImageMatchingTests"
TEST_NAMES = frozenset({
    "test_native_coordinates_recover_translation_and_inverted_contrast",
    "test_subpixel_correspondences_are_not_integer_rounded",
    "test_uniform_and_periodic_content_are_ambiguous",
    "test_masks_exclude_overlay_and_input_arrays_are_unchanged",
    "test_mismatched_dimensions_preserve_native_coordinates",
})
REQUIRED_VERSIONS = {"numpy": "1.26.4", "scipy": "1.11.4"}
EXPECTED_COUNTS = {
    "testsRun": 5, "passed": 5, "skipped": 0, "failures": 0, "errors": 0,
    "expectedFailures": 0, "unexpectedSuccesses": 0,
}


def imported_versions() -> dict[str, str]:
    """Read versions from imported modules, not installation metadata."""
    return {name: importlib.import_module(name).__version__ for name in REQUIRED_VERSIONS}


def exact_suite() -> unittest.TestSuite:
    """Only the explicitly authorized five tests may enter this job."""
    root = str(Path(__file__).absolute().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    suite = unittest.defaultTestLoader.loadTestsFromName(TEST_CLASS)
    identifiers = [test.id() for test in suite]
    expected = {f"{TEST_CLASS}.{name}" for name in TEST_NAMES}
    if len(identifiers) != 5 or set(identifiers) != expected:
        raise ValueError("the frozen synthetic test selection is not exactly the required five")
    return suite


def evaluate_result(result: unittest.TestResult) -> dict:
    """unittest success with skips/expected failures is not an acceptable PASS."""
    counts = {"testsRun": result.testsRun}
    for field in ("skipped", "failures", "errors", "expectedFailures", "unexpectedSuccesses"):
        counts[field] = len(getattr(result, field))
    counts["passed"] = counts["testsRun"] - sum(
        counts[field] for field in counts if field != "testsRun"
    )
    valid = all(type(counts[field]) is int and counts[field] == value
                for field, value in EXPECTED_COUNTS.items())
    return {"test_class": TEST_CLASS, **counts, "status": "PASS" if valid else "BLOCKED"}


def main() -> int:
    report = {"test_class": TEST_CLASS, "status": "BLOCKED"}
    try:
        versions = imported_versions()
        report["imported_versions"] = versions
        if versions != REQUIRED_VERSIONS:
            raise ValueError("imported dependency versions differ from the exact CI pins")
        result = unittest.TextTestRunner(verbosity=2).run(exact_suite())
        report.update(evaluate_result(result))
    except (ImportError, AttributeError, TypeError, ValueError) as exc:
        report["reason"] = f"synthetic contract runner rejected configuration: {type(exc).__name__}"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
