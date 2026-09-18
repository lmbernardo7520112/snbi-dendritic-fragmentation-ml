"""Mandatory memory-only FRAG scientific contracts; skips never count as PASS."""

import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    versions = {name: importlib.import_module(name).__version__ for name in ("numpy", "scipy")}
    if versions != {"numpy": "1.26.4", "scipy": "1.11.4"}:
        raise RuntimeError("existing pinned synthetic dependencies required")
    suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_ti2r_frag_registration")
    expected = suite.countTestCases()
    if expected != 16:
        raise RuntimeError("mandatory synthetic contract selection incomplete")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    categories = ("skipped", "failures", "errors", "expectedFailures", "unexpectedSuccesses")
    counts = {key: len(getattr(result, key)) for key in categories}
    counts.update(testsRun=result.testsRun, passed=result.testsRun - sum(counts.values()))
    passed = counts["passed"] == expected == result.testsRun
    print(json.dumps({"status": "PASS" if passed else "BLOCKED", "versions": versions, **counts}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
