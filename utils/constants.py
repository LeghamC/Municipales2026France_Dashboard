from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

RAW_FILES = {
    1: RAW_DIR / "municipales2026_t1_communes.csv",
    2: RAW_DIR / "municipales2026_t2_communes.csv",
}
GEOJSON_FILE = RAW_DIR / "departements.geojson"
PROCESSED_FILE = PROCESSED_DIR / "communes_clean.parquet"

DATAGOUV_API = "https://www.data.gouv.fr/api/1"
DATASET_SLUGS = {
    1: [
        "elections-municipales-2026-resultats-du-premier-tour",
        "elections-municipales-2026-resultats-du-1er-tour",
    ],
    2: ["elections-municipales-2026-resultats-du-second-tour"],
}
DATASET_PAGES = {
    1: "https://www.data.gouv.fr/datasets/?q=Elections%20municipales%202026%20r%C3%A9sultats%20premier%20tour",
    2: "https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-second-tour",
}
SEARCH_QUERIES = {
    1: "Elections municipales 2026 résultats du premier tour",
    2: "Elections municipales 2026 résultats du second tour",
}
GEOJSON_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/"
    "departements-version-simplifiee.geojson"
)

SOURCE_LABEL = "Ministère de l'Intérieur - Élections municipales 2026 (15 & 22 March 2026) - data.gouv.fr"
LICENSE_LABEL = "Licence Ouverte / Open Licence 2.0 (Etalab)"
ROUND_DATES = {1: "15 March 2026", 2: "22 March 2026"}

SIZE_BINS = [0, 100, 500, 1_000, 5_000, 20_000, 100_000, float("inf")]
SIZE_LABELS = [
    "< 100",
    "100–499",
    "500–999",
    "1,000–4,999",
    "5,000–19,999",
    "20,000–99,999",
    "≥ 100,000",
]

OVERSEAS_CODES = {"ZA": "971", "ZB": "972", "ZC": "973", "ZD": "974", "ZM": "976"}

DEPT_TO_REGION = {
    **{d: "Auvergne-Rhône-Alpes" for d in ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"]},
    **{d: "Bourgogne-Franche-Comté" for d in ["21", "25", "39", "58", "70", "71", "89", "90"]},
    **{d: "Bretagne" for d in ["22", "29", "35", "56"]},
    **{d: "Centre-Val de Loire" for d in ["18", "28", "36", "37", "41", "45"]},
    **{d: "Corse" for d in ["2A", "2B"]},
    **{d: "Grand Est" for d in ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"]},
    **{d: "Hauts-de-France" for d in ["02", "59", "60", "62", "80"]},
    **{d: "Île-de-France" for d in ["75", "77", "78", "91", "92", "93", "94", "95"]},
    **{d: "Normandie" for d in ["14", "27", "50", "61", "76"]},
    **{d: "Nouvelle-Aquitaine" for d in ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"]},
    **{d: "Occitanie" for d in ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"]},
    **{d: "Pays de la Loire" for d in ["44", "49", "53", "72", "85"]},
    **{d: "Provence-Alpes-Côte d'Azur" for d in ["04", "05", "06", "13", "83", "84"]},
    "971": "Outre-mer",
    "972": "Outre-mer",
    "973": "Outre-mer",
    "974": "Outre-mer",
    "976": "Outre-mer",
}

METRICS = {
    "abstention_rate": {
        "label": "Abstention rate",
        "short": "Abstention",
        "help": "Abstentions ÷ registered voters. Higher = more registered voters stayed home.",
    },
    "blank_null_share": {
        "label": "Blank + null ballots (share of voters)",
        "short": "Blank + null",
        "help": "(Blank + null ballots) ÷ voters. A signal of voters who turned up but rejected every option.",
    },
    "participation_rate": {
        "label": "Participation rate",
        "short": "Participation",
        "help": "Voters ÷ registered voters.",
    },
}
