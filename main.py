from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
import requests

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN") # Meta থেকে পাবে
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") # তুমি যেটা ইচ্ছা দেবে

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_learning(question, answer):
    try:
        supabase.table("teach_data").insert({
            "question": question.lower().strip(),
            "answer": answer
        }).execute()
        return "Got it, I learned that! ✅"
    except:
        return "I already know this question."

def get_answer(question):
    result = supabase.table("teach_data") \
     .select("answer") \
     .eq("question", question.lower().strip()) \
     .execute()
    if result.data:
        return result.data[0]["answer"]
    return None

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v18.0/me/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Verification for Meta
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Unauthorized", 403

    # Receive message
    if request.method == "POST":
        data = request.get_json()
        try:
            entry = data["entry"][0]["changes"][0]["value"]
            if "messages" in entry:
                message = entry["messages"][0]
                from_number = message["from"]
                msg_text = message["text"]["body"]

                # Teach command check
                if msg_text.lower().startswith("teach "):
                    try:
                        q, a = msg_text[6:].split("|", 1)
                        reply = save_learning(q, a)
                    except:
                        reply = "Wrong format. Use: teach question | answer"
                else:
                    answer = get_answer(msg_text)
                    reply = answer if answer else "I don't know that. Teach me: teach question | answer"

                send_whatsapp_message(from_number, reply)
        except Exception as e:
            print("Error:", e)

        return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
