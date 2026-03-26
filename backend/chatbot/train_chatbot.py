import os
import json
import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

CSV_PATH = os.path.join(DATA_DIR, "final_chatbot_training_dataset.csv")
MODEL_PATH = os.path.join(MODELS_DIR, "intent_pipeline.joblib")
REPORT_PATH = os.path.join(MODELS_DIR, "training_report.json")


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'label' columns.")

    X = df["text"].astype(str)
    y = df["label"].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            analyzer="char_wb",
            ngram_range=(1, 5),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            max_iter=4000,
            class_weight="balanced",
            C=2.0
        ))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    joblib.dump(pipeline, MODEL_PATH)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": accuracy,
            "total_samples": len(df),
            "report": report
        }, f, indent=2)

    print("Training complete")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()