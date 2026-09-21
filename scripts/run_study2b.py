"""Explicit Study2-B entry; preflight alone opens no source or receipt."""
import argparse
import json
from pathlib import Path

from snbi_fragmentation.study2b_execution import preflight, run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('legacy', 'full'))
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = preflight(root, args.mode) if args.preflight_only else run(root, args.mode)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get('status', result.get('STUDY2_B')) == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
