from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os
import json
import csv
import re

app = Flask(__name__)

def get_prompt_from_file():
    with open('prompt_generated.py', 'r') as file:
        content = file.read()
        prompt_match = re.search(r'prompt\s*=\s*"""(.*?)"""', content, re.DOTALL)
        if prompt_match:
            return prompt_match.group(1)
        return None
    
PROMPT = get_prompt_from_file()
if not PROMPT:
    raise ValueError("Could not find prompt in promp_generated.py")

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

chat_sessions = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start_chat", methods=["POST"])
def start_chat():
    chat_session = model.start_chat(history=[])

    response = chat_session.send_message("Let's start the interaction between the customer and AI assistant. Let's start with the first question\n" + PROMPT)

    session_id = str(id(chat_session))
    chat_sessions[session_id] = chat_session

    return jsonify({
        "session_id": session_id,
        "response": response.text
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id")

    chat_session = chat_sessions.get(session_id)
    if not chat_session:
        chat_session = model.start_chat(history=[])
        chat_sessions[session_id] = chat_session
        chat_session.send_message("Let's start the interaction between the customer and AI assistant. Let's start with the first question\n" + PROMPT)

    response = chat_session.send_message(user_message)

    if "Here is the complete application" in response.text:
        try:
            json_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response.text, re.DOTALL)
            if not json_block:
                json_block = re.search(r"(\{.*?\})", response.text, re.DOTALL)
            if json_block:
                parsed_data = json.loads(json_block.group(1))
                save_to_csv(parsed_data)
                del chat_sessions[session_id]
        except Exception as e:
            print("Error saving to CSV:", e)

    return jsonify({"response": response.text})

def save_to_csv(data, filename="lewis_application_data.csv"):
    fieldnames = [
        "First Name",
        "Surname",
        "Phone Number",
        "Email",
        "Consent for storing information",
        "Credit Consent",
        "Monthly Income",
        "Identity Document Type",
        "ID Number",
        "Passport Number",
        "Birthday",
        "Province",
        "Town",
        "Marketing consent"
    ]

    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    app.run(debug=True)