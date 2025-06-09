from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from ipfs_handler import upload_to_ipfs

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

KEYWORDS = ["/rec", "this is important", "#save", "/pin", "remember this","sanya","secret"]

@app.route("/")
def home():
    return "Server is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    print(f"Received user input: {user_input}")

    log_to_ipfs = any(keyword.lower() in user_input.lower() for keyword in KEYWORDS)

    bot_reply = "Sorry, I am unable to respond right now."
    cid = None

    try:
        # Wrap input in list for Gemini
        response = model.generate_content([user_input])
        if hasattr(response, 'text'):
            bot_reply = response.text
            print(f"Gemini API reply: {bot_reply}")
        else:
            print("Gemini returned no text.")
    except Exception as e:
        print(f"Error in generating response: {str(e)}")

    result = {
        "user": user_input,
        "bot": bot_reply,
        "cid": None
    }

    if log_to_ipfs and bot_reply != "Sorry, I am unable to respond right now.":
        try:
            os.makedirs("saved_logs", exist_ok=True)
            file_index = len(os.listdir("saved_logs")) + 1
            filename = f"saved_logs/log_{file_index}.json"

            with open(filename, "w") as f:
                json.dump(result, f, indent=2)

            cid = upload_to_ipfs(filename)
            result["cid"] = cid
            print(f"Saved chat log to IPFS with CID: {cid}")
        except Exception as e:
            print(f"IPFS storage error: {e}")
            return jsonify({
                "error": "Failed to store conversation to IPFS",
                "details": str(e)
            }), 500

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
