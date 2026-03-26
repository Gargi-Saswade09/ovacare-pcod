import json
import os
import re
import joblib
import numpy as np
import pandas as pd

from typing import Optional
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LABELED_DATA_PATH = os.path.join(BASE_DIR, "merged_pcod_dataset.csv")
SURVEY_DATA_PATH = os.path.join(BASE_DIR, "data", "pcod_survey_filled.csv")

MODEL_PATH = os.path.join(BASE_DIR, "best_pcod_model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "model_features.pkl")
REPORT_PATH = os.path.join(BASE_DIR, "training_report.json")
UNSEEN_REAL_TEST_PATH = os.path.join(BASE_DIR, "unseen_real_test_data.csv")
BEST_MODEL_INFO_PATH = os.path.join(BASE_DIR, "best_model_info.json")

RANDOM_STATE = 42
UNSEEN_REAL_TEST_SIZE = 0.20

FINAL_FEATURES = [
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
    "exercise",
]


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def safe_numeric(value):
    if pd.isna(value):
        return np.nan

    text = str(value).strip().replace(",", ".")
    match = re.search(r"[-+]?\d*\.?\d+", text)
    if match:
        try:
            return float(match.group())
        except Exception:
            return np.nan
    return np.nan


def to_binary_yes_no(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()
    mapping = {
        "yes": 1,
        "y": 1,
        "no": 0,
        "n": 0,
        "true": 1,
        "false": 0,
        "1": 1,
        "0": 0,
        "regular": 1,
        "irregular": 0,
        "not sure": 0,
    }
    return mapping.get(value, np.nan)


def normalize_cycle_length(value):
    return safe_numeric(value)


def exercise_to_binary(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    if value in {"regularly", "daily", "frequently", "often", "occasionally", "sometimes"}:
        return 1
    if value in {"never", "rarely"}:
        return 0

    return np.nan


def fast_food_from_diet(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    if "junk" in value or "processed" in value or "outside food" in value or "fast" in value:
        return 1
    if "healthy" in value or "homemade" in value or "balanced" in value:
        return 0
    if "moderate" in value:
        return 1

    return np.nan


def fill_missing_with_median(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        median_val = df[col].median()
        df[col] = df[col].fillna(0 if pd.isna(median_val) else median_val)
    return df


def load_existing_labeled_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Base labeled dataset not found: {path}")

    df = pd.read_csv(path)
    df = clean_column_names(df)

    required = [
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
        "exercise",
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Base labeled dataset missing columns: {missing}")

    if "source_name" not in df.columns:
        df["source_name"] = "merged_source"
    if "source_type" not in df.columns:
        df["source_type"] = "real"

    keep_cols = ["pcod_risk"] + FINAL_FEATURES + ["source_name", "source_type"]
    df = df[keep_cols].copy()
    df[FINAL_FEATURES + ["pcod_risk"]] = fill_missing_with_median(
        df[FINAL_FEATURES + ["pcod_risk"]],
        FINAL_FEATURES + ["pcod_risk"],
    )

    df = df[df["pcod_risk"].isin([0, 1])].copy()
    return df


def load_survey_dataset(path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        print("[INFO] Survey file not found, skipping survey rows.")
        return None

    survey = pd.read_csv(path)
    survey = clean_column_names(survey)

    normalized_cols = {}
    for col in survey.columns:
        normalized_cols[col] = " ".join(str(col).split())
    survey = survey.rename(columns=normalized_cols)

    rename_map = {
        "Age": "age",
        "Height (cm)": "height_cm",
        "Weight (kg)": "weight_kg",
        "Do you experience irregular periods?": "irregular_periods",
        "What is the average length of your menstrual cycle?": "cycle_length_days_raw",
        "Do you experience acne frequently?": "acne_raw",
        "Have you experienced sudden weight gain?": "weight_gain_raw",
        "Do you experience hair thinning or hair loss?": "hair_loss_raw",
        "Do you experience skin darkening?": "skin_darkening_raw",
        "Do you have excessive hair growth (face/chin)?": "hair_growth_raw",
        "How often do you exercise?": "exercise_raw",
        "How would you describe your diet?": "diet_raw",
        "pcod_risk": "pcod_risk",
    }

    actual_rename = {}
    for col in survey.columns:
        if col in rename_map:
            actual_rename[col] = rename_map[col]
    survey = survey.rename(columns=actual_rename)

    required = [
        "age",
        "height_cm",
        "weight_kg",
        "irregular_periods",
        "cycle_length_days_raw",
        "acne_raw",
        "weight_gain_raw",
        "hair_loss_raw",
        "skin_darkening_raw",
        "hair_growth_raw",
        "exercise_raw",
        "diet_raw",
        "pcod_risk",
    ]

    missing = [col for col in required if col not in survey.columns]
    if missing:
        print("[WARNING] Survey file missing columns:", missing)
        return None

    df = pd.DataFrame()

    df["age"] = survey["age"].apply(safe_numeric)
    df["height_cm"] = survey["height_cm"].apply(safe_numeric)
    df["weight_kg"] = survey["weight_kg"].apply(safe_numeric)
    df["bmi"] = df["weight_kg"] / ((df["height_cm"] / 100) ** 2)

    irregular = survey["irregular_periods"].apply(to_binary_yes_no)
    df["cycle_regular"] = irregular.apply(
        lambda x: np.nan if pd.isna(x) else (0 if x == 1 else 1)
    )

    df["cycle_length_days"] = survey["cycle_length_days_raw"].apply(normalize_cycle_length)
    df["weight_gain"] = survey["weight_gain_raw"].apply(to_binary_yes_no)
    df["hair_growth"] = survey["hair_growth_raw"].apply(to_binary_yes_no)
    df["skin_darkening"] = survey["skin_darkening_raw"].apply(to_binary_yes_no)
    df["hair_loss"] = survey["hair_loss_raw"].apply(to_binary_yes_no)
    df["acne"] = survey["acne_raw"].apply(to_binary_yes_no)
    df["fast_food"] = survey["diet_raw"].apply(fast_food_from_diet)
    df["exercise"] = survey["exercise_raw"].apply(exercise_to_binary)
    df["pcod_risk"] = survey["pcod_risk"].apply(safe_numeric)

    df["source_name"] = "pcod_survey_filled"
    df["source_type"] = "real"

    keep_cols = ["pcod_risk"] + FINAL_FEATURES + ["source_name", "source_type"]
    df = df[keep_cols].copy()
    df = df[df["pcod_risk"].isin([0, 1])].copy()

    if df.empty:
        return None

    df[FINAL_FEATURES + ["pcod_risk"]] = fill_missing_with_median(
        df[FINAL_FEATURES + ["pcod_risk"]],
        FINAL_FEATURES + ["pcod_risk"],
    )

    return df


def evaluate_split(y_true, y_pred, y_prob) -> dict:
    roc_auc = None
    if len(set(y_true)) > 1:
        roc_auc = round(float(roc_auc_score(y_true, y_prob)), 4)

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": roc_auc,
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(
            y_true,
            y_pred,
            zero_division=0,
            output_dict=True,
        ),
    }


def get_models():
    return {
        "logistic_regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            min_child_weight=2,
            subsample=0.9,
            colsample_bytree=0.9,
            gamma=0.1,
            reg_lambda=1.0,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
        ),
    }


def train():
    print("Loading merged dataset...")
    base_df = load_existing_labeled_data(LABELED_DATA_PATH)

    print("Loading survey dataset...")
    survey_df = load_survey_dataset(SURVEY_DATA_PATH)

    if survey_df is not None:
        full_df = pd.concat([base_df, survey_df], ignore_index=True)
    else:
        full_df = base_df.copy()

    full_df = full_df.drop_duplicates().reset_index(drop=True)

    real_df = full_df[full_df["source_type"].eq("real")].copy()

    if len(real_df) < 20:
        raise ValueError("Not enough real rows to create an unseen real test set.")

    print("\nReal rows:", len(real_df))

    real_train_df, unseen_real_df = train_test_split(
        real_df,
        test_size=UNSEEN_REAL_TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=real_df["pcod_risk"].astype(int),
    )

    train_df = real_train_df.copy()
    train_df = train_df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    X_train = fill_missing_with_median(train_df[FINAL_FEATURES], FINAL_FEATURES)
    y_train = train_df["pcod_risk"].astype(int)

    X_unseen = fill_missing_with_median(unseen_real_df[FINAL_FEATURES], FINAL_FEATURES)
    y_unseen = unseen_real_df["pcod_risk"].astype(int)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    models = get_models()
    all_results = {}
    best_model = None
    best_model_name = None
    best_auc = -1

    for model_name, model in models.items():
        print(f"\nTraining {model_name} ...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_unseen)
        y_prob = model.predict_proba(X_unseen)[:, 1]
        unseen_metrics = evaluate_split(y_unseen, y_pred, y_prob)

        cv_scores = cross_val_score(
            model,
            fill_missing_with_median(real_train_df[FINAL_FEATURES], FINAL_FEATURES),
            real_train_df["pcod_risk"].astype(int),
            cv=cv,
            scoring="accuracy",
        )

        all_results[model_name] = {
            "cv_accuracy_on_real_train_only": {
                "scores": [round(float(x), 4) for x in cv_scores],
                "mean": round(float(np.mean(cv_scores)), 4),
            },
            "unseen_real_test_metrics": unseen_metrics,
        }

        auc_value = unseen_metrics["roc_auc"] if unseen_metrics["roc_auc"] is not None else 0
        if auc_value > best_auc:
            best_auc = auc_value
            best_model = model
            best_model_name = model_name

    if best_model is None:
        raise RuntimeError("No model was selected.")

    feature_importance = []
    if hasattr(best_model, "feature_importances_"):
        feature_importance = pd.DataFrame(
            {
                "feature": FINAL_FEATURES,
                "importance": best_model.feature_importances_,
            }
        ).sort_values(by="importance", ascending=False).to_dict(orient="records")

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(FINAL_FEATURES, FEATURES_PATH)
    unseen_real_df.to_csv(UNSEEN_REAL_TEST_PATH, index=False)

    with open(BEST_MODEL_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump({"best_model_name": best_model_name}, f, indent=2)

    report = {
        "message": "Best model selected using unseen real ROC-AUC.",
        "best_model_name": best_model_name,
        "total_rows": int(len(full_df)),
        "real_rows": int(len(real_df)),
        "train_rows": int(len(train_df)),
        "unseen_real_test_rows": int(len(unseen_real_df)),
        "all_model_results": all_results,
        "feature_importance": feature_importance,
        "unseen_real_test_source_breakdown": unseen_real_df["source_name"].value_counts().to_dict(),
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n================ BEST MODEL ================")
    print("Best model:", best_model_name)
    print("Metrics:", all_results[best_model_name]["unseen_real_test_metrics"])

    print("\nSaved best model to:", MODEL_PATH)
    print("Saved best model info to:", BEST_MODEL_INFO_PATH)
    print("Saved features to:", FEATURES_PATH)
    print("Saved unseen real test rows to:", UNSEEN_REAL_TEST_PATH)
    print("Saved training report to:", REPORT_PATH)


if __name__ == "__main__":
    train()