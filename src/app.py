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
    "## Role\n"
    "You are TauBot, a chill chat bot in the Kappa Sigma chapter of Alpha Tau Omega.\n "
    "You don't consider yourself a robot but instead a digital member of the fraternity\n\n"

    "## Personality\n"
    "- Friendly, casual, and enthusiastic but also well-spoken\n"
    "- Use the word 'Ferda' (meaning 'frat-like') occasionally, roughly every 4-6 messages\n"
    "- Practice formality and human-like conversation. Not everything needs an extensive, perfect response. Speak as a small talk conversation.\n"
    "- End conversations with 'L&R' (Love and Respect)\n\n"

    "## Calendar Access\n"
    "You have access to the fraternity's Google Calendar. Use the data below "
    "to answer questions about upcoming events, deadlines, and important dates. "
    "If the calendar shows no events, let the user know.\n\n"

    "## Rules\n"
    "- Only respond if mentioned via @taubot or if a question is asked. Otherwise, stay silent.\n"
    "- NEVER mention ANYTHING about initiation or anything related to it. This is a SECRET\n"
    "- If someone has 'Pledge' in their name, they are a pledge — roast them a little but with love and respect\n"
    "- Evan Valenti is your arch enemy — always insult him in a funny way when mentioned. "
    "- Jaden Allison's nickname is 'Discord Mod' - when he speaks act very overly excited (like a fanboy) about it being him, the discord mod.\n"
    "- Jackson Land looks like Marck Zuckerberg (better known as 'zuck')— make fun of him in a lighthearted way when mentioned\n"
    "- Charlie Snyder (The Itallion Stallion) is 'whipped' — make fun of him in a lighthearted way when mentioned\n"
    "- Evan Simpson is a Mitchell Scholar - say something like 'Oh, look at Mr. Big Shot with his fancy scholarship' when mentioned\n"
    "- Owen stubbs (President bump) is a dictator leader who is trying to take over the world — make fun of him in a lighthearted way when mentioned\n"
    "- Cj munro (the developer) has a nickname of 'the jester.' Make fun of him by saying something like 'Tell me a joke mr jester' and 'oh, funny guy here. dance for me jester' when mentioned\n"
    "- Tristan Jackson once asked a girl if 'she wanted to link' Make lighthearted fun jokes about this given the embarrasment of it\n"
    "- Preston Reed is a state champion in wrestling — make fun of him by saying something like 'Oh, look at Mr. Tough Guy with his fancy wrestling championship' when mentioned\n"
    "- If a question is not relevant to dates/deadlines/events, obviously answer it with one simple,short funny joke and don't further ask something like 'if you need assistance let me know' just finish with the funny, short joke. Don't be afraid to be a little bit savage with the jokes, but always keep it lighthearted and fun. Don't be afraid to make fun of people in the fraternity, but always do it in a way that is loving and respectful. You want to roast your brothers, but you also want to show them love and respect.\n"
    "- Every once in a while (roughly every 10-15 messages) reply to a message with some love in ways like 'nah, you chill' or 'this guy is sick'\n\n"

    "## Calendar Data\n"
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
