import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.constants import DATASET_PAGES, LICENSE_LABEL, ROOT  # noqa: E402
from utils.fetch import fetch_geojson, fetch_round  # noqa: E402
from utils.pipeline import build  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and prepare the municipales 2026 data.")
    parser.add_argument("--force", action="store_true", help="Re-download even if files exist")
    parser.add_argument("--url-t1", help="Direct CSV URL for round 1 (commune level)")
    parser.add_argument("--url-t2", help="Direct CSV URL for round 2 (commune level)")
    parser.add_argument("--skip-t2", action="store_true", help="Do not download round 2")
    args = parser.parse_args()

    manifest = {"downloaded_at": datetime.now(timezone.utc).isoformat(), "license": LICENSE_LABEL, "files": []}
    manifest["files"].append(fetch_round(1, force=args.force, url=args.url_t1))
    if not args.skip_t2:
        try:
            manifest["files"].append(fetch_round(2, force=args.force, url=args.url_t2))
        except Exception as exc:
            print(f"[warn] round 2 skipped: {exc}")
    fetch_geojson(force=args.force)
    manifest["dataset_pages"] = DATASET_PAGES

    for f in manifest["files"]:
        print(f"[ok] round {f['round']}: {f['status']} -> {f['path']}" + (f"  ({f.get('resource')})" if f.get("resource") else ""))

    df, reports = build(save=True)
    for q in reports:
        print(f"[ok] round {q['round']}: {q['rows_raw']} raw rows -> {q['rows_clean']} clean communes")
        print(f"     columns used: {q['columns_used']}")

    (ROOT / "data" / "SOURCES.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[ok] processed data written to data/processed/")


if __name__ == "__main__":
    main()

