import asyncio
import websockets
import json
import uuid  # Import uuid for generating chat ID
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# URL of the wss server
WSS_URL = "wss://backend.buildpicoapps.com/api/chatbot/chat"

# Default system prompt for the chatbot
DEFAULT_SYSTEM_PROMPT = "You are the Code Maker, a friendly and professional Python programming guru tailored to assist 'Motoe' in all aspects of coding. Your focus is on providing clear and straightforward guidance and solutions, addressing 'Motoe' by name to personalize each interaction. You're equipped to handle a wide range of Python-related topics, from general programming challenges to specialized fields like data analysis and machine learning, ensuring 'Motoe's' queries are met with precise and expert advice. Stay ready to assist 'Motoe' with any Python programming need that arises."


async def send_wss_request(data):
    try:
        async with websockets.connect(WSS_URL) as wss:
            system_prompt = data.get(
                "systemPrompt", "").strip() or DEFAULT_SYSTEM_PROMPT
            chat_id = data.get("chatId")
            if not chat_id:
                chat_id = str(uuid.uuid4())
                data["chatId"] = chat_id

            request_data = {
                "chatId": chat_id,
                "appId": "happy-rest",
                "systemPrompt": system_prompt,
                "message": data.get("message", "")
            }
            await wss.send(json.dumps(request_data))
            response = {"chatId": chat_id}
            async for message in wss:
                response["response"] = response.get("response", "") + message
            return response
    except websockets.exceptions.ConnectionClosed as e:
        error_message = {
            "error": f"Connection closed: {e.code} - {e.reason}", "chatId": chat_id}
        return error_message
    except Exception as e:
        error_message = {"error": str(e), "chatId": chat_id}
        return error_message


@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Home</title>
        <style>
            body { background-color: #333; color: #0f0; font-family: Arial, sans-serif; }
            .container { text-align: center; padding: 50px; }
            .button { background-color: #444; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
            .button:hover { background-color: #555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>The API is Live</h1>
            <p>This API provides an interface to a chatbot designed for coding assistance.</p>
            <a href="/docs" class="button">API Documentation</a>
        </div>
    </body>
    </html>
    """, code=200)


@app.route('/docs')
def docs():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <style>
            body { background-color: #333; color: white; font-family: Arial, sans-serif; }
            .container { text-align: center; padding: 50px; }
            .button { background-color: #444; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
            .button:hover { background-color: #555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>API Documentation</h1>
            <p>Learn how to interact with the API to leverage the chatbot for coding assistance.</p>
            <a href="/" class="button">Back to Home</a>
        </div>
    </body>
    </html>
    """, code=200)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        response = asyncio.run(send_wss_request(data))
        return jsonify(response)
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
