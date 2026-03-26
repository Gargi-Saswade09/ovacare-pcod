import csv
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "chatbot_intents.csv")

random.seed(42)

INTENT_PATTERNS = {
    "greeting": [
        "hello", "hi", "hey", "good morning", "good evening",
        "can you help me", "i need help", "hello bot"
    ],
    "stress_general": [
        "how to reduce stress", "stress relief", "i feel stressed",
        "how to calm my mind", "stress management", "mental stress help",
        "how to relax", "i am overwhelmed", "stress problem",
        "how can i feel calm", "my mind is tired"
    ],
    "pcod_general": [
        "what is pcod", "what is pcos", "pcod symptoms",
        "how to manage pcod", "pcos problem", "irregular periods and acne",
        "weight gain in pcos", "pcod basics", "why does pcod happen",
        "what are signs of pcod"
    ],
    "diet_pcod": [
        "diet for pcod", "food for pcos", "what to eat in pcod",
        "pcod meal plan", "best breakfast for pcos", "healthy food for pcod",
        "foods to avoid in pcod", "pcos diet chart", "what should i eat in pcos",
        "best diet for hormonal balance"
    ],
    "diet_stress": [
        "food for stress", "diet for stress relief", "what should i eat when stressed",
        "foods that reduce stress", "healthy snacks for stress",
        "best diet for stress", "what to drink for stress", "foods that calm the mind"
    ],
    "exercise_pcod": [
        "exercise for pcod", "best workout for pcos", "pcod exercise plan",
        "walking for pcos", "yoga for pcod", "gym workout for pcos",
        "strength training for pcos", "home workout for pcos"
    ],
    "exercise_stress": [
        "exercise for stress", "stress relief exercise", "breathing exercise",
        "yoga for stress", "walking for stress relief", "how to relax physically",
        "quick exercise to calm down", "best workout for mental stress"
    ],
    "emergency": [
        "i want to hurt myself", "i am not safe", "i want to disappear",
        "i feel like giving up", "i may harm myself", "i cannot cope anymore"
    ]
}

PREFIXES = [
    "", "please ", "can you ", "help me with ", "tell me ", "guide me on ", "i need "
]

SUFFIXES = [
    "", " today", " for beginners", " naturally", " safely", " at home"
]

HINGLISH_VARIANTS = [
    ["pcod me kya khana chahiye", "diet_pcod"],
    ["stress kam kaise kare", "stress_general"],
    ["pcod ke symptoms kya hai", "pcod_general"],
    ["stress ke liye exercise", "exercise_stress"],
    ["pcod ke liye workout", "exercise_pcod"],
    ["stress me kya khana chahiye", "diet_stress"]
]


def generate_rows():
    rows = []

    for label, phrases in INTENT_PATTERNS.items():
        for phrase in phrases:
            for prefix in PREFIXES:
                for suffix in SUFFIXES:
                    text = f"{prefix}{phrase}{suffix}".strip()
                    rows.append([text, label])

                    typo_text = (
                        text.replace("stress", "strees")
                        .replace("pcos", "pcod")
                        .replace("exercise", "excercise")
                    )
                    rows.append([typo_text, label])

    for text, label in HINGLISH_VARIANTS:
        rows.append([text, label])

    random.shuffle(rows)
    return rows


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    rows = generate_rows()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)

    print(f"Dataset created: {OUTPUT_FILE}")
    print(f"Total rows: {len(rows)}")


if __name__ == "__main__":
    main()