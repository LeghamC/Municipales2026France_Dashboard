import re

import numpy as np
import pandas as pd

from utils.constants import DEPT_TO_REGION, OVERSEAS_CODES, SIZE_BINS, SIZE_LABELS
from utils.io import _norm

ALIASES = {
    "dep_code": ["codedepartement", "codedudepartement", "codedpt", "coddpt", "departementcode", "codedep"],
    "dep_name": ["libelledepartement", "libelledudepartement", "libdpt", "departement", "nomdepartement"],
    "com_code": ["codecommune", "codedelacommune", "codcom", "codecirconscription", "codcirelec", "codeinsee", "codecommuneinsee"],
    "com_name": ["libellecommune", "libelledelacommune", "libcom", "libellecirconscription", "libcirelec", "commune", "nomcommune"],
    "inscrits": ["inscrits", "nombredinscrits", "nombredinscrit"],
    "abstentions": ["abstentions", "abstention"],
    "votants": ["votants", "nombredevotants"],
    "blancs": ["blancs", "nombreblancs", "votesblancs"],
    "nuls": ["nuls", "nombrenuls", "votesnuls"],
    "exprimes": ["exprimes", "nombredesuffrage", "suffragesexprimes"],
}
REQUIRED = ["dep_code", "com_code", "inscrits", "votants"]
COUNT_COLS = ["inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes"]


class SchemaError(ValueError):
    pass


def map_columns(columns: list[str]) -> dict[str, str]:
    usable = [c for c in columns if "%" not in c and "pourcent" not in _norm(c)]
    normed = {}
    for c in usable:
        normed.setdefault(_norm(c), c)
    mapping = {}
    for canon, candidates in ALIASES.items():
        for cand in candidates:
            if cand in normed:
                mapping[canon] = normed[cand]
                break
    missing = [c for c in REQUIRED if c not in mapping]
    if missing:
        raise SchemaError(
            f"Could not find required column(s) {missing}. Columns in the file: {columns[:40]}. "
            "Add the right name to ALIASES in utils/prep.py."
        )
    return mapping


def list_vote_columns(columns: list[str]) -> list[str]:
    return [c for c in columns if "%" not in c and re.fullmatch(r"voix\d+", _norm(c))]


def to_number(s: pd.Series) -> pd.Series:
    cleaned = (
        s.astype("string")
        .str.replace(r"[\s  ]", "", regex=True)
        .str.replace(",", ".", regex=False)
        .replace("", pd.NA)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def normalize_dep(code: str) -> str:
    code = str(code).strip().upper()
    code = OVERSEAS_CODES.get(code, code)
    if code.isdigit() and len(code) < 2:
        code = code.zfill(2)
    return code


def build_insee(dep: str, com: str) -> str:
    com = str(com).strip().upper()
    if len(com) >= 5:
        return com[-5:]
    if len(dep) == 3:
        return dep + com.zfill(3)[-2:]
    return dep + com.zfill(3)


def size_band(inscrits: pd.Series) -> pd.Series:
    return pd.cut(inscrits, bins=SIZE_BINS, labels=SIZE_LABELS, right=False)


def clean_round(raw: pd.DataFrame, round_no: int) -> tuple[pd.DataFrame, dict]:
    mapping = map_columns(list(raw.columns))
    vote_cols = list_vote_columns(list(raw.columns))
    df = raw[list(mapping.values())].rename(columns={v: k for k, v in mapping.items()}).copy()

    quality = {"round": round_no, "rows_raw": int(len(raw)), "columns_used": mapping, "excluded": []}

    for col in ("dep_code", "com_code", "dep_name", "com_name"):
        if col in df:
            df[col] = df[col].astype("string").str.strip()
    for col in COUNT_COLS:
        df[col] = to_number(df[col]) if col in df else np.nan

    missing = []
    for col in ["dep_code", "com_code", "com_name"] + COUNT_COLS:
        if col in mapping:
            series = df[col]
            n = int(series.isna().sum() + (series.astype("string") == "").sum()) if series.dtype == "string" else int(series.isna().sum())
            missing.append({"column": col, "source_column": mapping[col], "missing": n})
        else:
            missing.append({"column": col, "source_column": "— not in file —", "missing": None})
    quality["missing"] = missing

    if vote_cols:
        votes = raw[vote_cols].apply(to_number)
        df["n_lists"] = (votes.fillna(0) > 0).sum(axis=1).astype("Int64")
    else:
        df["n_lists"] = pd.array([pd.NA] * len(df), dtype="Int64")

    df["abstentions_derived"] = df["abstentions"].isna()
    df["abstentions"] = df["abstentions"].fillna(df["inscrits"] - df["votants"])

    def drop(mask: pd.Series, reason: str):
        nonlocal df
        mask = mask.astype("boolean").fillna(True).to_numpy(dtype=bool)
        n = int(mask.sum())
        if n:
            quality["excluded"].append({"reason": reason, "rows": n})
        df = df.loc[~mask].copy()

    drop(df["dep_code"].isna() | (df["dep_code"] == "") | df["com_code"].isna() | (df["com_code"] == ""), "Missing department or commune code")
    drop(df["inscrits"].isna() | (df["inscrits"] <= 0), "Zero or missing registered voters")
    drop(df["votants"].isna() | (df["votants"] > df["inscrits"]), "Voters missing or greater than registered voters")

    df["dep_code"] = df["dep_code"].map(normalize_dep)
    df["insee"] = [build_insee(d, c) for d, c in zip(df["dep_code"], df["com_code"])]
    df["region"] = df["dep_code"].map(DEPT_TO_REGION)
    drop(df["region"].isna(), "Outside the 101 departments (e.g. other overseas collectivities)")

    dup = df.duplicated(subset="insee", keep="first")
    quality["duplicates"] = int(dup.sum())
    drop(dup, "Duplicate commune code (kept first occurrence)")

    checks = []
    def check(name: str, tested: pd.Series, failed: pd.Series):
        checks.append({"check": name, "tested": int(tested.sum()), "failed": int((tested & failed).sum())})

    has_abs = ~df["abstentions_derived"]
    has_abs = has_abs.to_numpy(dtype=bool)
    check("Voters + abstentions = registered", has_abs, (df["votants"] + df["abstentions"]) != df["inscrits"])
    has_ballots = df[["blancs", "nuls", "exprimes"]].notna().all(axis=1)
    check("Blank + null + valid votes = voters", has_ballots, (df["blancs"] + df["nuls"] + df["exprimes"]) != df["votants"])
    check("Rates between 0 % and 100 %", df["inscrits"] > 0, (df["votants"] / df["inscrits"] > 1) | (df["votants"] < 0))
    quality["checks"] = checks
    quality["abstentions_derived"] = int(df["abstentions_derived"].sum())

    for col in COUNT_COLS:
        df[col] = df[col].astype("float64")
    df["round"] = round_no
    df["size_band"] = size_band(df["inscrits"])
    if "dep_name" not in df:
        df["dep_name"] = df["dep_code"]
    if "com_name" not in df:
        df["com_name"] = df["insee"]
    df = add_rates(df)
    quality["rows_clean"] = int(len(df))

    keep = ["round", "insee", "com_name", "dep_code", "dep_name", "region", "size_band", "n_lists",
            "inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes",
            "abstention_rate", "participation_rate", "blank_null_share"]
    return df[keep].reset_index(drop=True), quality


def add_rates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["abstention_rate"] = df["abstentions"] / df["inscrits"]
    df["participation_rate"] = df["votants"] / df["inscrits"]
    df["blank_null_share"] = (df["blancs"].fillna(0) + df["nuls"].fillna(0)) / df["votants"].where(df["votants"] > 0)
    return df


def aggregate(df: pd.DataFrame, by: list[str] | str | None = None) -> pd.DataFrame:
    sums = ["inscrits", "abstentions", "votants", "blancs", "nuls"]
    if by is None:
        out = df[sums].sum().to_frame().T
        out["communes"] = len(df)
    else:
        out = df.groupby(by, observed=True)[sums].sum().reset_index()
        out["communes"] = df.groupby(by, observed=True).size().values
    return add_rates(out)


def runoff_comparison(df: pd.DataFrame) -> pd.DataFrame:
    t1 = df[df["round"] == 1].set_index("insee")
    t2 = df[df["round"] == 2].set_index("insee")
    common = t1.index.intersection(t2.index)
    if common.empty:
        return pd.DataFrame()
    out = t1.loc[common, ["com_name", "dep_code", "dep_name", "region", "size_band", "inscrits"]].copy()
    out["participation_t1"] = t1.loc[common, "participation_rate"]
    out["participation_t2"] = t2.loc[common, "participation_rate"]
    out["blank_null_t1"] = t1.loc[common, "blank_null_share"]
    out["blank_null_t2"] = t2.loc[common, "blank_null_share"]
    out["delta_participation_pts"] = (out["participation_t2"] - out["participation_t1"]) * 100
    return out.reset_index()
