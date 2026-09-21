"""Bounded metadata planning and one governed Study2-C benchmark."""
import argparse
import json
from pathlib import Path
from snbi_fragmentation.study2c_execution import preflight, prepare_plan, run


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("plan","run","preflight"))
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    result={"plan":prepare_plan,"run":run,"preflight":preflight}[args.mode](root)
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),flush=True)
    return 0 if result.get("status",result.get("STUDY2_C"))=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
