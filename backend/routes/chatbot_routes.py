from flask import Blueprint, request, jsonify
from chatbot.chat_service import chatbot_service

chatbot_bp = Blueprint("chatbot_bp", __name__)

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    result = chatbot_service.get_response(message)
    return jsonify(result)