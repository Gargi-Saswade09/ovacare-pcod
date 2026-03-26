import csv
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_PATH = os.path.join(BASE_DIR, "merged_pcod_dataset.csv")

FINAL_COLUMNS = [
    "pcod_risk",
    "age",
    "bmi",
    "cycle_regular",
    "cycle_length_days",
    "weight_gain",
    "hair_growth",
    "skin_darkening",
    "hair_loss",
    "acne",
    "fast_food",
    "exercise"
]

META_COLUMNS = ["source_name", "source_type"]


def detect_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        sample = f.read(4096)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except Exception:
        if "\t" in sample and sample.count("\t") > sample.count(","):
            return "\t"
        return ","


def read_csv_auto(path: str) -> pd.DataFrame:
    delimiter = detect_delimiter(path)
    return pd.read_csv(path, sep=delimiter, encoding="utf-8-sig")


def standardize_binary(series: pd.Series) -> pd.Series:
    mapping = {
        "Y": 1, "N": 0,
        "Yes": 1, "No": 0,
        "yes": 1, "no": 0,
        "TRUE": 1, "FALSE": 0,
        True: 1, False: 0,
        "regular": 1, "irregular": 0,
        "R": 1, "I": 0,
        "r": 1, "i": 0
    }

    cleaned = series.replace(mapping)
    cleaned = pd.to_numeric(cleaned, errors="coerce").fillna(0)
    return cleaned.apply(lambda x: 1 if x >= 1 else 0).astype(int)


def clean_common(df: pd.DataFrame, source_name: str, source_type: str) -> pd.DataFrame:
    df = df.copy()

    for col in FINAL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[FINAL_COLUMNS].copy()

    for col in FINAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    binary_cols = [
        "pcod_risk",
        "cycle_regular",
        "weight_gain",
        "hair_growth",
        "skin_darkening",
        "hair_loss",
        "acne",
        "fast_food",
        "exercise"
    ]

    for col in binary_cols:
        df[col] = standardize_binary(df[col])

    numeric_cols = [c for c in FINAL_COLUMNS if c not in binary_cols]
    for col in numeric_cols:
        median_val = df[col].median()
        df[col] = df[col].fillna(0 if pd.isna(median_val) else median_val)

    df["source_name"] = source_name
    df["source_type"] = source_type

    return df[FINAL_COLUMNS + META_COLUMNS]


def load_dataset_a(path: str) -> pd.DataFrame:
    df = read_csv_auto(path)

    rename_map = {
        "PCOS (Y/N)": "pcod_risk",
        " Age (yrs)": "age",
        "Age (yrs)": "age",
        "BMI": "bmi",
        "Cycle(R/I)": "cycle_regular",
        "Cycle length(days)": "cycle_length_days",
        "Weight gain(Y/N)": "weight_gain",
        "hair growth(Y/N)": "hair_growth",
        "Skin darkening (Y/N)": "skin_darkening",
        "Hair loss(Y/N)": "hair_loss",
        "Pimples(Y/N)": "acne",
        "Fast food (Y/N)": "fast_food",
        "Reg.Exercise(Y/N)": "exercise"
    }

    df = df.rename(columns=rename_map)

    if "cycle_regular" in df.columns:
        df["cycle_regular"] = pd.to_numeric(df["cycle_regular"], errors="coerce")
        df["cycle_regular"] = df["cycle_regular"].map({2: 1, 4: 0}).fillna(df["cycle_regular"])

    return clean_common(df, source_name="dataset_a", source_type="real")


def load_dataset_b(path: str) -> pd.DataFrame:
    df = read_csv_auto(path)
    return clean_common(df, source_name="dataset_b", source_type="real")


def load_kaggle(path: str) -> pd.DataFrame:
    df = read_csv_auto(path)

    rename_map = {
        "PCOS (Y/N)": "pcod_risk",
        " Age (yrs)": "age",
        "Age (yrs)": "age",
        "BMI": "bmi",
        "Cycle(R/I)": "cycle_regular",
        "Cycle length(days)": "cycle_length_days",
        "Weight gain(Y/N)": "weight_gain",
        "hair growth(Y/N)": "hair_growth",
        "Skin darkening (Y/N)": "skin_darkening",
        "Hair loss(Y/N)": "hair_loss",
        "Pimples(Y/N)": "acne",
        "Fast food (Y/N)": "fast_food",
        "Reg.Exercise(Y/N)": "exercise"
    }

    df = df.rename(columns=rename_map)

    if "cycle_regular" in df.columns:
        df["cycle_regular"] = pd.to_numeric(df["cycle_regular"], errors="coerce")
        df["cycle_regular"] = df["cycle_regular"].map({2: 1, 4: 0}).fillna(df["cycle_regular"])

    return clean_common(df, source_name="pcod_kaggle", source_type="real")


def load_synthetic(path: str, max_rows: int = 1200) -> pd.DataFrame:
    df = read_csv_auto(path)
    df = clean_common(df, source_name="pcod_synthetic_5000", source_type="synthetic")

    if len(df) > max_rows:
        df = df.sample(max_rows, random_state=42)

    return df.reset_index(drop=True)


def merge_all() -> pd.DataFrame:
    files = {
        "dataset_a": os.path.join(DATA_DIR, "dataset_a.csv"),
        "dataset_b": os.path.join(DATA_DIR, "dataset_b.csv"),
        "pcod_kaggle": os.path.join(DATA_DIR, "pcod_kaggle.csv"),
        "pcod_synthetic_5000": os.path.join(DATA_DIR, "pcod_synthetic_5000.csv")
    }

    df_a = load_dataset_a(files["dataset_a"])
    df_b = load_dataset_b(files["dataset_b"])
    df_k = load_kaggle(files["pcod_kaggle"])
    df_s = load_synthetic(files["pcod_synthetic_5000"])

    merged = pd.concat([df_a, df_b, df_k, df_s], ignore_index=True)
    merged = merged.drop_duplicates().reset_index(drop=True)

    merged.to_csv(OUTPUT_PATH, index=False)

    print("Merged dataset created successfully.")
    print("Saved to:", OUTPUT_PATH)
    print("Shape:", merged.shape)

    print("\nSource distribution:")
    print(merged["source_type"].value_counts())

    print("\nClass distribution:")
    print(merged["pcod_risk"].value_counts())

    return merged


if __name__ == "__main__":
    merge_all()