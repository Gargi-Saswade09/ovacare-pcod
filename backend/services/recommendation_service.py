def generate_diet_plan(pcod_result=None, stress_result=None):
    if pcod_result and stress_result:
        if pcod_result == "High Risk of PCOD" and stress_result == "High":
            return [
                "Eat high-fiber meals with oats, vegetables, lentils, and fruits.",
                "Reduce sugar, bakery foods, and processed snacks.",
                "Include protein in every meal: paneer, sprouts, eggs, dal, tofu.",
                "Add calming foods like nuts, seeds, curd, banana, and herbal tea.",
                "Do not skip meals and drink enough water."
            ]
        if pcod_result == "High Risk of PCOD":
            return [
                "Use a low-glycemic diet with high fiber and balanced protein.",
                "Avoid refined carbs and sugary drinks.",
                "Add leafy vegetables and anti-inflammatory foods."
            ]
        return [
            "Follow balanced meals and include fruits, salads, and protein.",
            "Use stress-supportive foods like seeds, nuts, curd, and fresh fruits."
        ]

    if pcod_result and not stress_result:
        if pcod_result == "High Risk of PCOD":
            return [
                "Take hormone-friendly balanced meals.",
                "Reduce sugar, deep-fried foods, and refined flour.",
                "Increase vegetables, protein, and hydration."
            ]
        return [
            "Maintain a balanced and clean diet.",
            "Eat on time and stay hydrated."
        ]

    if stress_result and not pcod_result:
        if stress_result == "High":
            return [
                "Avoid too much caffeine and junk food.",
                "Eat simple home-cooked meals on time.",
                "Add banana, curd, nuts, seeds, and hydration."
            ]
        return [
            "Maintain regular healthy meals.",
            "Eat enough protein, vegetables, and fruits."
        ]

    return [
        "Common healthy recommendation: balanced meals, regular hydration, less junk food.",
        "Take stress quiz and PCOD test for personalized diet recommendations."
    ]


def generate_exercise_plan(pcod_result=None, stress_result=None):
    if pcod_result and stress_result:
        if pcod_result == "High Risk of PCOD" and stress_result == "High":
            return [
                "20 to 30 minutes brisk walking daily.",
                "10 minutes breathing exercise.",
                "Gentle yoga for hormonal balance.",
                "Avoid extreme workouts; consistency is better."
            ]
        if pcod_result == "High Risk of PCOD":
            return [
                "30 minutes walk or cycling at least 5 days a week.",
                "Beginner strength training 2 to 3 times per week.",
                "Stretching and yoga for flexibility."
            ]
        return [
            "Light cardio, stretching, yoga, and weekly strength sessions."
        ]

    if pcod_result and not stress_result:
        if pcod_result == "High Risk of PCOD":
            return [
                "Brisk walking, cycling, yoga, and light strength training."
            ]
        return [
            "Regular moderate movement for at least 30 minutes."
        ]

    if stress_result and not pcod_result:
        if stress_result == "High":
            return [
                "Walking, light yoga, meditation, and breathing exercises."
            ]
        return [
            "Regular walking and mobility work."
        ]

    return [
        "Common exercise recommendation: 30 minutes daily movement, stretching, and walking.",
        "Take stress quiz and PCOD test for personalized exercise plans."
    ]