from flask import Blueprint, request, jsonify

from service.chat_services import get_chatbot_response


chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "success": False,
                "reply": "Please enter a question."
            }), 400

        reply = get_chatbot_response(user_message)

        return jsonify({
            "success": True,
            "reply": reply
        })

    except Exception as e:

        import traceback

        print("CHAT ROUTE ERROR:", repr(e))
        traceback.print_exc()

        return jsonify({
            "success": False,
            "reply": "Chatbot backend error."
        }), 500