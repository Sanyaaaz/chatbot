from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from ipfs_handler import upload_to_ipfs, fetch_from_ipfs

load_dotenv()
app = Flask(__name__)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Keywords to trigger IPFS logging
KEYWORDS = ["/rec", "this is important", "#save", "/pin", "remember this"]
@app.route("/")
def home():
    return "Server is running!"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data["message"]
    log_to_ipfs = any(keyword in user_input.lower() for keyword in KEYWORDS)

    response = model.generate_content(user_input)
    bot_reply = response.text

    result = {"user": user_input, "bot": bot_reply}

    if log_to_ipfs:
        filename = f"saved_logs/log_{len(os.listdir('saved_logs')) + 1}.json"
        with open(filename, "w") as f:
            json.dump(result, f)
        cid = upload_to_ipfs(filename)
        result["cid"] = cid

    return jsonify(result)

@app.route("/retrieve", methods=["POST"])
def retrieve():
    cid = request.json.get("cid")
    try:
        data = fetch_from_ipfs(cid)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    os.makedirs("saved_logs", exist_ok=True)
    app.run(debug=True)
