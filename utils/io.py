import csv
import io
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

from utils.constants import GEOJSON_FILE, RAW_FILES


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def score_resource(resource: dict) -> float:
    title = _norm(resource.get("title", "")) + _norm(resource.get("description", "") or "")
    fmt = (resource.get("format") or "").lower()
    if fmt not in {"csv", "txt"}:
        return -1e9
    score = 0.0
    if "commune" in title:
        score += 10
    for bad in ("bureau", "bv", "elus", "elu", "polynesie", "arrondissement", "secteur", "candidat"):
        if bad in title:
            score -= 8
    if "franceentiere" in title:
        score += 4
    score += min((resource.get("filesize") or 0) / 1e7, 2)
    return score


def pick_commune_resource(resources: list[dict]) -> dict | None:
    ranked = sorted(resources, key=score_resource, reverse=True)
    if not ranked or score_resource(ranked[0]) <= 0:
        return None
    return ranked[0]


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _sniff_sep(header_line: str) -> str:
    counts = {sep: header_line.count(sep) for sep in (";", ",", "\t")}
    return max(counts, key=counts.get)


def read_ministry_csv(path: Path) -> pd.DataFrame:
    text = _read_text(path)
    header_line = text.split("\n", 1)[0]
    sep = _sniff_sep(header_line)
    rows = list(csv.reader(io.StringIO(text), delimiter=sep))
    header, body = [h.strip() for h in rows[0]], rows[1:]
    seen: dict[str, int] = {}
    for i, h in enumerate(header):
        if h in seen:
            seen[h] += 1
            header[i] = f"{h}.{seen[h]}"
        else:
            seen[h] = 0
    n = len(header)
    body = [(r + [""] * n)[:n] for r in body if any(cell.strip() for cell in r)]
    return pd.DataFrame(body, columns=header, dtype=str)


def load_raw(round_no: int) -> pd.DataFrame | None:
    path = RAW_FILES[round_no]
    if not path.exists():
        return None
    return read_ministry_csv(path)


def _signed_area(ring: list) -> float:
    return sum(x1 * y2 - x2 * y1 for (x1, y1, *_), (x2, y2, *_) in zip(ring, ring[1:] + ring[:1])) / 2


def _rewind_polygon(poly: list) -> list:
    out = []
    for i, ring in enumerate(poly):
        clockwise = _signed_area(ring) < 0
        want_clockwise = i == 0
        out.append(ring if clockwise == want_clockwise else ring[::-1])
    return out


def rewind_for_plotly(geo: dict) -> dict:
    for feat in geo.get("features", []):
        g = feat.get("geometry") or {}
        if g.get("type") == "Polygon":
            g["coordinates"] = _rewind_polygon(g["coordinates"])
        elif g.get("type") == "MultiPolygon":
            g["coordinates"] = [_rewind_polygon(p) for p in g["coordinates"]]
    return geo


def load_geojson() -> dict | None:
    if not GEOJSON_FILE.exists():
        return None
    return rewind_for_plotly(json.loads(GEOJSON_FILE.read_text(encoding="utf-8")))

