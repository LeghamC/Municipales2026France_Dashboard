import json

import pandas as pd

from utils.constants import PROCESSED_DIR, PROCESSED_FILE, RAW_FILES
from utils.io import load_raw
from utils.prep import clean_round

QUALITY_FILE = PROCESSED_DIR / "quality_report.json"


def build(save: bool = True) -> tuple[pd.DataFrame, list[dict]]:
    frames, reports = [], []
    for round_no in (1, 2):
        raw = load_raw(round_no)
        if raw is None:
            if round_no == 1:
                raise FileNotFoundError(f"Missing {RAW_FILES[1]} - run `python scripts/download_data.py` first.")
            continue
        clean, quality = clean_round(raw, round_no)
        frames.append(clean)
        reports.append(quality)
    df = pd.concat(frames, ignore_index=True)
    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out = df.copy()
        out["size_band"] = out["size_band"].astype(str)
        out.to_parquet(PROCESSED_FILE, index=False)
        QUALITY_FILE.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
    return df, reports


def load_processed() -> tuple[pd.DataFrame, list[dict]] | None:
    if not (PROCESSED_FILE.exists() and QUALITY_FILE.exists()):
        return None
    df = pd.read_parquet(PROCESSED_FILE)
    reports = json.loads(QUALITY_FILE.read_text(encoding="utf-8"))
    return df, reports

