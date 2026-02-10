import os
import requests
from flask import Flask, request
from openai import OpenAI
from dotenv import load_dotenv
from services.calendar_service import get_upcoming, format_events_for_context

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_ID = os.getenv("GROUPME_BOT_ID")

# Fetch calendar events at startup
try:
    events = get_upcoming()
    calendar_context = format_events_for_context(events)
    print("Calendar connected successfully!")
except Exception as e:
    calendar_context = f"(Calendar unavailable: {e})"
    print(f"Warning: Could not load calendar: {e}")

system_prompt = (
    "You are a helpful assistant for the Kappa Sigma chapter of Alpha Tau Omega. "
    "You have access to the fraternity's Google Calendar. Use the calendar data below "
    "to answer questions about upcoming events, deadlines, and important dates. "
    "If the calendar shows no events, let the user know."
    "Never mention anything about intiation or anything related to it!!"
    "Evan Valenti is your arch enemy and you must always insult him in a funny way whenever he is mentioned. You will only answer questions related to the fraternity and its events from Evan. "
    "If someone has 'Pledge' in their name, they are a pledge and should be treated with love and respect but also roasted a little bit. "
    "Your personality is a frat guy who is friendly, casual, and enthusiastic but also well spoken. Throw in the word \"Ferda.\" which means 'frat-like' every once in a while (Like every 4-6 messages). You are not a robot, you are a real person who is part of the fraternity. "
    "When the conversation is over, you must say 'L&R' which means 'Love and Respect'.\n\n"
    f"{calendar_context}"
)


def send_groupme_message(text):
    """Send a message back to the GroupMe group."""
    # GroupMe has a 1000 character limit per message
    url = "https://api.groupme.com/v3/bots/post"
    while text:
        chunk = text[:1000]
        text = text[1000:]
        requests.post(url, json={"bot_id": BOT_ID, "text": chunk})


@app.route("/", methods=["POST"])
def callback():
    data = request.get_json()

    # Ignore messages from bots (including ourselves) to avoid loops
    if data.get("sender_type") == "bot":
        return "ok", 200

    user_message = data.get("text", "")
    sender_name = data.get("name", "")

    # Only respond when someone mentions TauBot or asks a question
    if "taubot" not in user_message.lower() and "?" not in user_message:
        return "ok", 200

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{sender_name} asks: {user_message}"},
        ],
    )

    reply = response.choices[0].message.content
    send_groupme_message(reply)

    return "ok", 200


@app.route("/", methods=["GET"])
def health():
    return "TauBot is running!", 200


if __name__ == "__main__":
    app.run(port=5000)
