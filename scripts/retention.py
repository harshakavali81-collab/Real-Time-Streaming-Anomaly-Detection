"""Safe-by-default local data retention. Requires --execute for deletion."""
import argparse
import json
from time import time
from src.sinks.store import Store

def prune(days: int, execute: bool = False, db_url: str | None = None) -> dict:
    if not 1 <= days <= 3650:
        raise ValueError("days must be 1..3650")
    result = Store(db_url).prune_before(time()-days*86400, execute=execute)
    return {"retention_days": days, **result,
            "notice": "DELETED matching demo rows and their audit history" if execute else
                      "DRY RUN ONLY: supply --execute to delete matched rows"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--db", default=None)
    args = parser.parse_args()
    print(json.dumps(prune(args.days, args.execute, args.db), indent=2))
