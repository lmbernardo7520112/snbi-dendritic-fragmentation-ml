"""One future author-authorized Study3 invocation; no recovery execution mode."""
import json
from pathlib import Path

from snbi_fragmentation.study3_execution import run


def main():
    result = run(Path(__file__).absolute().parents[1])
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result.get("STUDY3") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
