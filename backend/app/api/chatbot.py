"""
Chatbot API endpoints
"""
from flask import Blueprint, request, jsonify
from app.services.chatbot_service import ChatbotService

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/v1/chatbot')


@chatbot_bp.route('/message', methods=['POST'])
def send_message():
    """
    Send a message to the chatbot

    Request body:
        {
            "message": "What cookies do you have?"
        }

    Returns:
        {
            "type": "response_type",
            "message": "Bot response",
            "products": [...],  // Optional
            "suggestions": [...]  // Optional
        }
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        user_message = data['message'].strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get chatbot response
        response = ChatbotService.get_response(user_message)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'type': 'error',
            'message': 'Sorry, I encountered an error. Please try again!',
            'error': str(e)
        }), 500


@chatbot_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """
    Get conversation starter suggestions

    Returns:
        {
            "suggestions": [...]
        }
    """
    return jsonify({
        'suggestions': [
            'Hi! What can you help me with?',
            'Show me birthday cookies',
            'What cookies are in stock?',
            'I need gluten-free options',
            'Show me chocolate cookies',
            'What are your best sellers?'
        ]
    }), 200
