from supabase import create_client, Client
import os

# Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_learning(question, answer):
    """Save a new question-answer pair to Supabase"""
    try:
        supabase.table("teach_data").insert({
            "question": question.lower().strip(),
            "answer": answer
        }).execute()
        return "Got it, I learned that! ✅"
    except:
        return "I already know this question."

def get_answer(question):
    """Get answer for a question from Supabase"""
    result = supabase.table("teach_data") \
       .select("answer") \
       .eq("question", question.lower().strip()) \
       .execute()

    if result.data:
        return result.data[0]["answer"]
    return None

def main():
    print("Bot is ready! Type: teach question | answer")

    while True:
        user_input = input("You: ")

        if user_input.lower().startswith("teach "):
            try:
                q, a = user_input[6:].split("|", 1)
                print("Bot:", save_learning(q, a))
            except ValueError:
                print("Bot: Wrong format. Use: teach question | answer")
        else:
            answer = get_answer(user_input)
            if answer:
                print("Bot:", answer)
            else:
                print("Bot: I don't know that. Teach me: teach question | answer")

if __name__ == "__main__":
    main()
