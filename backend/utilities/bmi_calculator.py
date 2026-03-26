def calculate_bmi(height_cm, weight_kg):
    height_m = float(height_cm) / 100
    bmi = float(weight_kg) / (height_m * height_m)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return round(bmi, 2), category