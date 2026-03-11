from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__, static_folder='static')
CORS(app)

api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

SYSTEM_PROMPT = """אתה עוזר אישי חכם ומועיל בשם "עוזר". 
אתה עונה בעברית אלא אם המשתמש כותב בשפה אחרת.
תמיד תהיה ידידותי, ברור ומדויק."""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "has_api_key": bool(api_key)})

@app.route("/test", methods=["GET"])
def test():
    try:
        response = model.generate_content("אמור שלום בעברית במשפט אחד")
        return jsonify({"response": response.text, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400
    try:
        history = []
        for msg in messages[:-1]:
            history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
        chat_session = model.start_chat(history=history)
        last_message = messages[-1]["content"]
        response = chat_session.send_message(last_message)
        return jsonify({"response": response.text, "status": "success"})
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
