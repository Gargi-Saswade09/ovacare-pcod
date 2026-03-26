import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "final_chatbot_training_dataset.csv")

VALID_LABELS = {
    "greeting",
    "pcod_general",
    "stress_general",
    "diet_pcod",
    "diet_stress",
    "exercise_pcod",
    "exercise_stress",
    "combined_pcod_stress",
    "website_help",
    "period_general",
    "period_heavy",
    "period_irregular",
    "out_of_scope",
    "emergency"
}

frames = []

def load_labeled_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"Skipping missing file: {filename}")
        return None

    df = pd.read_csv(path)

    if "text" in df.columns and "label" in df.columns:
        temp = df[["text", "label"]].copy()
        temp["text"] = temp["text"].astype(str).str.strip()
        temp["label"] = temp["label"].astype(str).str.strip()
        return temp

    print(f"Skipping {filename}: text,label columns not found")
    return None

for filename in [
    "chatbot_intents.csv",
    "ovacare_chatbot_dataset_2000.csv",
    "natural_phrases_addon.csv"
]:
    df = load_labeled_csv(filename)
    if df is not None:
        frames.append(df)

counsel_path = os.path.join(DATA_DIR, "counsel_chat_cleaned.csv")
if os.path.exists(counsel_path):
    counsel_df = pd.read_csv(counsel_path)

    if "text" in counsel_df.columns and "label" in counsel_df.columns:
        temp = counsel_df[["text", "label"]].copy()
        temp["text"] = temp["text"].astype(str).str.strip()
        temp["label"] = temp["label"].astype(str).str.strip()
        frames.append(temp)

    elif "question" in counsel_df.columns:
        temp = pd.DataFrame()
        temp["text"] = counsel_df["question"].astype(str).str.strip()
        temp["label"] = "stress_general"
        frames.append(temp)

if not frames:
    raise ValueError("No valid datasets found.")

final_df = pd.concat(frames, ignore_index=True)

final_df = final_df.dropna()
final_df = final_df[final_df["text"] != ""]
final_df = final_df.drop_duplicates()
final_df = final_df[final_df["label"].isin(VALID_LABELS)]

final_df.to_csv(OUTPUT_PATH, index=False)

print("Final dataset created successfully")
print("Saved to:", OUTPUT_PATH)
print("Total rows:", len(final_df))
print("\nLabel counts:\n", final_df["label"].value_counts())