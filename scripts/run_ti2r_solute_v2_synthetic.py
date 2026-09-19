"""Strict V2-D synthetic contracts; no experimental buffers are read."""

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
        raise RuntimeError("synthetic dependency pins differ")
    suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_ti2r_solute_v2_calibration")
    count = suite.countTestCases()
    if count != 18:
        raise RuntimeError("V2-D synthetic contract set incomplete")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    counts = {name: len(getattr(result, name)) for name in
              ("skipped", "failures", "errors", "expectedFailures", "unexpectedSuccesses")}
    counts.update(testsRun=result.testsRun, passed=result.testsRun - sum(counts.values()))
    passed = counts["passed"] == count == result.testsRun
    print(json.dumps({"status": "PASS" if passed else "BLOCKED", "versions": versions, **counts}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
