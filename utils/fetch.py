from pathlib import Path

import requests

from utils.constants import DATAGOUV_API, DATASET_SLUGS, GEOJSON_FILE, GEOJSON_URL, RAW_FILES, SEARCH_QUERIES
from utils.io import _norm, pick_commune_resource

TIMEOUT = 60


def _get_json(url: str, params: dict | None = None) -> dict | None:
    r = requests.get(url, params=params, timeout=TIMEOUT)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def find_dataset(round_no: int) -> dict:
    for slug in DATASET_SLUGS[round_no]:
        ds = _get_json(f"{DATAGOUV_API}/datasets/{slug}/")
        if ds:
            return ds
    hits = _get_json(f"{DATAGOUV_API}/datasets/", {"q": SEARCH_QUERIES[round_no], "page_size": 20}) or {}
    wanted = "premiertour" if round_no == 1 else "secondtour"
    for ds in hits.get("data", []):
        title = _norm(ds.get("title", ""))
        org = _norm((ds.get("organization") or {}).get("name", ""))
        if "municipales2026" in title and (wanted in title or f"{round_no}ertour" in title) and "interieur" in org:
            return ds
    raise RuntimeError(
        f"Round {round_no}: dataset not found automatically. Download the commune-level CSV by hand "
        f"and save it as {RAW_FILES[round_no]}"
    )


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return dest


def fetch_round(round_no: int, force: bool = False, url: str | None = None) -> dict:
    dest = RAW_FILES[round_no]
    if dest.exists() and not force and not url:
        return {"round": round_no, "status": "cached", "path": str(dest)}
    if url:
        download(url, dest)
        return {"round": round_no, "status": "downloaded", "url": url, "path": str(dest)}
    ds = find_dataset(round_no)
    res = pick_commune_resource(ds.get("resources", []))
    if res is None:
        titles = [r.get("title") for r in ds.get("resources", [])]
        raise RuntimeError(f"Round {round_no}: no commune-level CSV among {titles}. Pass --url-t{round_no}.")
    download(res["url"], dest)
    return {
        "round": round_no,
        "status": "downloaded",
        "dataset": ds.get("title"),
        "dataset_page": ds.get("page"),
        "resource": res.get("title"),
        "url": res["url"],
        "path": str(dest),
    }


def fetch_geojson(force: bool = False) -> Path:
    if GEOJSON_FILE.exists() and not force:
        return GEOJSON_FILE
    return download(GEOJSON_URL, GEOJSON_FILE)

