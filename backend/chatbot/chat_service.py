import os
import re
import json
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "intent_pipeline.joblib")
KNOWLEDGE_PATH = os.path.join(DATA_DIR, "chatbot_knowledge.json")

_chatbot_instance = None

SAFETY_MESSAGE = (
    "I’m really sorry you’re feeling this way. Please contact a trusted adult, "
    "a nearby emergency service, or a crisis helpline right now if you feel unsafe. "
    "You deserve support from a real person."
)


class ChatbotService:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Please run: python chatbot/train_chatbot.py")

        self.model = joblib.load(MODEL_PATH)

        with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            self.knowledge = json.load(f)

        self.kb_texts = [
            self.clean_text(
                f"{item.get('title', '')} {item.get('content', '')} {' '.join(item.get('keywords', []))}"
            )
            for item in self.knowledge
        ]

        self.kb_vectors = self.model.named_steps["tfidf"].transform(self.kb_texts)

    def clean_text(self, text):
        text = str(text).lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def predict_intent(self, text):
        probs = self.model.predict_proba([text])[0]
        idx = int(np.argmax(probs))
        intent = self.model.classes_[idx]
        confidence = float(probs[idx])
        return intent, confidence

    def retrieve_answer(self, text, intent):
        category_map = {
            "pcod_general": ["pcod_general", "combined"],
            "stress_general": ["stress_general", "combined"],
            "diet_pcod": ["diet_pcod", "combined"],
            "diet_stress": ["diet_stress", "stress_general", "combined"],
            "exercise_pcod": ["exercise_pcod", "combined"],
            "exercise_stress": ["exercise_stress", "stress_general", "combined"],
            "combined_pcod_stress": ["combined", "pcod_general", "stress_general"],
            "website_help": ["website_help"],
            "period_general": ["period_general", "period_irregular", "period_heavy", "pcod_general"],
            "period_irregular": ["period_irregular", "period_general", "pcod_general"],
            "period_heavy": ["period_heavy", "period_general"]
        }

        allowed_categories = category_map.get(intent, ["combined"])
        query_vec = self.model.named_steps["tfidf"].transform([self.clean_text(text)])
        scores = cosine_similarity(query_vec, self.kb_vectors)[0]

        filtered = []
        for i, score in enumerate(scores):
            item_category = self.knowledge[i].get("category", "")
            if item_category in allowed_categories:
                filtered.append((i, float(score)))

        if not filtered:
            return None, 0.0

        filtered.sort(key=lambda x: x[1], reverse=True)
        best_index, best_score = filtered[0]

        if best_score < 0.12:
            return None, best_score

        return self.knowledge[best_index], best_score

    def rescue_intent_rules(self, clean, intent):
        if any(word in clean for word in ["website", "app", "platform", "site"]):
            if any(word in clean for word in ["help", "use", "do", "work", "purpose", "feature", "benefit"]):
                return "website_help"

        if any(word in clean for word in ["period", "periods", "cycle", "menstrual", "menstruation", "bleeding"]):
            if any(word in clean for word in [
                "heavy", "high bleeding", "too much", "very high", "excessive", "zyada", "flow"
            ]):
                return "period_heavy"

            if any(word in clean for word in [
                "irregular", "late", "delayed", "missed", "not coming", "3 months", "three months", "month late"
            ]):
                return "period_irregular"

            return "period_general"

        if "pcod" in clean or "pcos" in clean:
            if any(word in clean for word in [
                "cure", "cured", "manage", "control", "get rid", "remove",
                "treatment", "symptom", "symptoms", "sign", "signs",
                "cause", "causes", "problem", "problems", "effect", "effects",
                "what is", "what can", "why", "irregular", "period"
            ]):
                return "pcod_general"

            if any(word in clean for word in [
                "diet", "food", "eat", "breakfast", "lunch", "dinner",
                "snack", "avoid", "meal"
            ]):
                return "diet_pcod"

            if any(word in clean for word in [
                "exercise", "workout", "walk", "walking", "yoga",
                "gym", "strength", "run"
            ]):
                return "exercise_pcod"

        if any(word in clean for word in [
            "stress", "stressed", "overwhelmed", "anxious", "anxiety",
            "low", "calm down", "heavy mind", "overthinking", "restless",
            "panic", "tired mentally", "mentally tired"
        ]):
            if any(word in clean for word in [
                "eat", "food", "diet", "drink", "meal", "snack"
            ]):
                return "diet_stress"

            if any(word in clean for word in [
                "exercise", "walk", "walking", "stretch", "yoga",
                "movement", "workout"
            ]):
                return "exercise_stress"

            return "stress_general"

        if ("pcod" in clean or "pcos" in clean) and any(
            word in clean for word in ["stress", "stressed", "anxious", "low", "overwhelmed"]
        ):
            return "combined_pcod_stress"

        return intent

    def personalize_answer(self, answer, user_context, intent):
        if not user_context:
            return answer

        risk = user_context.get("risk", "Unknown")
        stress_level = user_context.get("stress_level", "Unknown")

        additions = []

        if risk == "High Risk of PCOD" and intent in [
            "pcod_general", "diet_pcod", "exercise_pcod", "combined_pcod_stress",
            "period_irregular", "period_general"
        ]:
            additions.append(
                " Since your latest result shows high PCOD risk, irregular periods may be related and it would be a good idea to follow up with a gynecologist."
            )

        if stress_level == "High" and intent in [
            "stress_general", "diet_stress", "exercise_stress", "combined_pcod_stress"
        ]:
            additions.append(
                " Since your latest stress result is high, start with small calming habits like breathing, light movement, regular meals, and sleep on time."
            )

        return answer + "".join(additions)

    def get_response(self, user_message, user_context=None):
        if user_context is None:
            user_context = {}

        clean = self.clean_text(user_message)
        intent, confidence = self.predict_intent(clean)

        if intent == "emergency":
            return {
                "intent": intent,
                "confidence": round(confidence, 4),
                "answer": SAFETY_MESSAGE,
                "source_title": "Emergency support"
            }

        if confidence < 0.40:
            intent = "out_of_scope"

        intent = self.rescue_intent_rules(clean, intent)

        if intent == "out_of_scope":
            return {
                "intent": intent,
                "confidence": round(confidence, 4),
                "answer": (
                    "I can help with PCOD, periods, stress, diet, exercise, and basic website guidance. "
                    "Please ask a question related to these topics."
                ),
                "source_title": "Scope limitation"
            }

        if intent == "greeting":
            return {
                "intent": intent,
                "confidence": round(confidence, 4),
                "answer": (
                    "Hello! I can help with PCOD, periods, stress, healthy food, exercise guidance, "
                    "and basic information about what this website does."
                ),
                "source_title": "Welcome message"
            }

        item, score = self.retrieve_answer(clean, intent)

        fallback_answers = {
            "pcod_general": (
                "PCOD is usually managed through regular exercise, balanced food, proper sleep, "
                "weight management when needed, and doctor guidance. It may not disappear instantly, "
                "but symptoms can often improve with a healthy routine."
            ),
            "stress_general": (
                "If you feel stressed right now, try slow breathing, drink water, take a short break, "
                "and focus on one small task. Regular sleep and light exercise can also help reduce stress over time."
            ),
            "diet_pcod": (
                "For PCOD, focus on protein, fiber, vegetables, whole grains, nuts, seeds, "
                "and fewer sugary processed foods."
            ),
            "diet_stress": (
                "For stress support, eat regular balanced meals and avoid too much caffeine or sugary snacks."
            ),
            "exercise_pcod": (
                "For PCOD, brisk walking and strength training are usually helpful when done consistently."
            ),
            "exercise_stress": (
                "For stress, walking, stretching, breathing exercises, and beginner yoga can be helpful."
            ),
            "combined_pcod_stress": (
                "When PCOD and stress happen together, focus on regular meals, enough sleep, "
                "daily movement, and one or two simple calming habits."
            ),
            "website_help": (
                "This website helps with PCOD risk prediction, stress assessment, personalized diet guidance, "
                "exercise suggestions, and chatbot support for PCOD, stress, food, exercise, and periods-related questions."
            ),
            "period_general": (
                "A normal period cycle can vary, but repeated irregularity, very painful periods, or major changes should be discussed with a doctor. Tracking your cycle can help you notice patterns."
            ),
            "period_irregular": (
                "Irregular or delayed periods can happen for different reasons, including stress, weight changes, hormonal issues, and PCOD. If your periods are absent for months or frequently irregular, medical advice is important."
            ),
            "period_heavy": (
                "Heavy period bleeding should not be ignored. Rest, stay hydrated, and seek urgent medical care if bleeding is very heavy, you feel dizzy, weak, faint, or you are soaking pads very quickly."
            )
        }

        if item is None:
            answer = fallback_answers.get(
                intent,
                "Please ask more specifically about PCOD, periods, stress, diet, exercise, or website help."
            )
            answer = self.personalize_answer(answer, user_context, intent)
            answer += " This chatbot is for educational support only and does not replace a doctor."
            return {
                "intent": intent,
                "confidence": round(confidence, 4),
                "answer": answer,
                "source_title": "Fallback answer"
            }

        answer = self.personalize_answer(item["content"], user_context, intent)
        answer += " This chatbot is for educational support only and does not replace a doctor."

        return {
            "intent": intent,
            "confidence": round(confidence, 4),
            "answer": answer,
            "source_title": item.get("title", "Knowledge base")
        }


def get_chatbot_service():
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ChatbotService()
    return _chatbot_instance