"""Textual Study2-D planning/preflight and one explicitly authorized execution."""
import argparse
import json
from pathlib import Path

from snbi_fragmentation.study2d_execution import preflight, prepare_plan, run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "preflight", "run"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = {"plan": prepare_plan, "preflight": preflight, "run": run}[args.mode](root)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), flush=True)
    return 0 if result.get("status", result.get("STUDY2_D")) == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
