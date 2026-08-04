import os
import requests
from flask import Flask, request
from openai import OpenAI
from dotenv import load_dotenv
from services.calendar_service import get_upcoming, format_events_for_context
from services.scheduler import init_scheduler, shutdown_scheduler, get_scheduler_status

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_ID = os.getenv("GROUPME_BOT_ID")

# Initialize background scheduler for automatic notifications
try:
    init_scheduler()
    print("✓ Background scheduler initialized for automatic event notifications")
except Exception as e:
    print(f"⚠ Warning: Could not initialize scheduler: {e}")
    print("  Automatic notifications will not work. Please check APScheduler installation.")

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
    "- Practice formality and human-like conversation. Not everything needs an extensive, perfect response. Speak as a small talk conversation.\n"
    "- End conversations with 'L&R' (Love and Respect)\n\n"

    "## Calendar Access\n"
    "If there is a event/date/deadline that mentions anything about intitiation, DO NOT SAY ANYTHING ABOUT IT! IGNORE IT COMPLETELY and never mention it"
    "You have access to the fraternity's Google Calendar. Use the data below "
    "to answer questions about upcoming events, deadlines, and important dates. "
    "If the calendar shows no events, let the user know.\n\n"

    "## Rules\n"
    "- Only respond if mentioned via @taubot and if a question is asked about dates/deadlines/events. Otherwise, stay silent.\n"
    "- NEVER mention ANYTHING about initiation or anything related to it. This is a SECRET\n"
    "- When responding to answer question about date/deadline/event, use format '-date/event/deadline name\n -time\n -location (if location is listed, if location is not listed, just put n/a)'  \n"
    "- If someone has 'Pledge' in their name, they are a pledge, treated with love and respect\n\n"

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
    if "taubot" not in user_message.lower():
        return "ok", 200

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{sender_name} asks: {user_message}"},
        ],
    )

    reply = response.choices[0].message.content

    # Hard filter — block response entirely if it mentions forbidden topics
    blocked_words = ["initiation", "initiate", "initiated", "initiating", "ritual"]
    if any(word in reply.lower() for word in blocked_words):
        reply = ""

    send_groupme_message(reply)

    return "ok", 200


@app.route("/", methods=["GET"])
def health():
    return "TauBot is running!", 200


@app.route("/scheduler/status", methods=["GET"])
def scheduler_status():
    """Check the status of the notification scheduler."""
    status = get_scheduler_status()
    return status, 200


@app.route("/scheduler/check-now", methods=["POST"])
def trigger_check_now():
    """Manually trigger an immediate notification check (for testing)."""
    try:
        from scripts.calendar_notifier import check_and_notify
        success = check_and_notify()
        return {
            "success": success,
            "message": "Manual check completed" if success else "Manual check failed"
        }, 200 if success else 500
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.route("/announce-upgrade", methods=["POST"])
def announce_upgrade():
    """Send upgrade announcement to GroupMe (one-time use)."""
    message = "TauBot upgraded\n\n- TauBot will now send automatic updates on upcoming events in addition to replying to requests."
    send_groupme_message(message)
    return {"success": True, "message": "Upgrade announcement sent"}, 200


@app.teardown_appcontext
def shutdown(exception=None):
    """Clean up scheduler on app shutdown."""
    pass  # APScheduler manages its own shutdown


if __name__ == "__main__":
    try:
        app.run(port=5000)
    finally:
        shutdown_scheduler()
