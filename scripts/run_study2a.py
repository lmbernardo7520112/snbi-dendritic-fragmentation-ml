"""Explicit entry point; no default scientific action."""
import argparse
import json
from pathlib import Path

from snbi_fragmentation.study2a_execution import EVIDENCE, preflight, run_full, run_legacy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--legacy", action="store_true")
    group.add_argument("--preflight", choices=("legacy", "full"))
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).absolute().parents[1]
    try:
        if args.preflight:
            result = preflight(root, args.preflight)
        elif args.legacy:
            result = run_legacy(root)
        else:
            result = run_full(root)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0 if result.get("status", result.get("STUDY2_A")) == "PASS" else 2
    except Exception as exc:
        consumed = any((root / EVIDENCE / name).exists()
                       for name in ("EXECUTION_RECEIPT.json", "LEGACY_RECEIPT.json"))
        print(json.dumps({"status": "BLOCKED_WITH_EXISTING_RECEIPT" if consumed else "BLOCKED_PREFLIGHT",
                          "error": type(exc).__name__, "detail": str(exc)}))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
