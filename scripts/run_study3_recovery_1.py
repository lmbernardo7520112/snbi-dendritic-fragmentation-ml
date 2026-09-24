"""One future explicitly authorized recovery invocation; preparation cannot run."""
import json
from pathlib import Path

from snbi_fragmentation.study3_execution import run_recovery_1


def main():
    result = run_recovery_1(Path(__file__).absolute().parents[1])
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result.get("STUDY3") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
