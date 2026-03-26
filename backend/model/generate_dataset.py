import pandas as pd
import numpy as np
import random

rows = 5000

data = []

for _ in range(rows):

    age = random.randint(18, 40)

    bmi = round(np.random.normal(25, 4), 2)

    cycle_regular = random.choice([0, 1])

    cycle_length_days = random.randint(21, 40)

    weight_gain = random.choice([0, 1])

    hair_growth = random.choice([0, 1])

    skin_darkening = random.choice([0, 1])

    hair_loss = random.choice([0, 1])

    acne = random.choice([0, 1])

    fast_food = random.choice([0, 1])

    exercise = random.choice([0, 1])

    risk_score = 0

    if bmi > 27:
        risk_score += 1

    if cycle_regular == 0:
        risk_score += 1

    if weight_gain == 1:
        risk_score += 1

    if hair_growth == 1:
        risk_score += 1

    if acne == 1:
        risk_score += 1

    if skin_darkening == 1:
        risk_score += 1

    if fast_food == 1:
        risk_score += 1

    if exercise == 0:
        risk_score += 1

    if risk_score >= 4:
        pcod_risk = 1
    else:
        pcod_risk = 0

    data.append([
        pcod_risk,
        age,
        bmi,
        cycle_regular,
        cycle_length_days,
        weight_gain,
        hair_growth,
        skin_darkening,
        hair_loss,
        acne,
        fast_food,
        exercise
    ])

columns = [
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

df = pd.DataFrame(data, columns=columns)

df.to_csv("data/pcod_synthetic_5000.csv", index=False)

print("Synthetic dataset generated successfully")
print("Rows:", len(df))