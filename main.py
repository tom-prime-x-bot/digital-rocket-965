from flask import Flask, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")

    if msg.lower().startswith("teach "):
        try:
            q, a = msg[6:].split("|", 1)
            return jsonify({"reply": save_learning(q, a)})
        except:
            return jsonify({"reply": "Wrong format. Use: teach question | answer"})
    else:
        answer = get_answer(msg)
        if answer:
            return jsonify({"reply": answer})
        else:
            return jsonify({"reply": "I don't know that. Teach me: teach question | answer"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
