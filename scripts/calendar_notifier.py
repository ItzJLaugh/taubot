"""
Script to check for upcoming calendar events and send GroupMe notifications.

Notification tiers:
- Tier 1 (14 days): Very important events (Mandatory, Brotherhood, Formal, Semi, Party, etc.)
- Tier 2 (7 days): Important events (Philanthropy, Service, Dues, etc.)
- Tier 3 (3 days): Other events (General meetings, etc.)
"""

import os
import sys
import datetime
from pathlib import Path

# Add parent directory to path to import services
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.calendar_service import get_upcoming
from src.services.notification_tracker import (
    init_db,
    has_notification_been_sent,
    record_notification_sent,
    cleanup_old_notifications,
)
import requests
from dotenv import load_dotenv

load_dotenv()

# Tier keywords for notification scheduling
TIER_1_KEYWORDS = ["mandatory", "brotherhood", "formal", "semi", "party", "rush", "alumni"]
TIER_2_KEYWORDS = ["philanthropy", "service", "dues", "volunteer", "community"]
TIER_3_KEYWORDS = []  # Default tier for all other events

RESTRICTED_KEYWORDS = ["initiation", "initiate", "initiated", "initiating"]


def get_event_tier(event):
    """Determine notification tier (1, 2, or 3) based on event keywords."""
    fields = [
        event.get("summary", ""),
        event.get("description", ""),
        event.get("location", "")
    ]
    combined = " ".join(fields).lower()

    if any(word in combined for word in RESTRICTED_KEYWORDS):
        return None  # Don't notify for restricted events

    if any(word in combined for word in TIER_1_KEYWORDS):
        return 1
    elif any(word in combined for word in TIER_2_KEYWORDS):
        return 2
    else:
        return 3


def days_until_event(event):
    """Calculate days until event starts."""
    start = event.get("start", "")

    # Parse ISO format datetime (handle both full datetime and date-only formats)
    try:
        if "T" in start:
            event_date = datetime.datetime.fromisoformat(start.replace("Z", "+00:00")).date()
        else:
            event_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

    today = datetime.datetime.utcnow().date()
    delta = (event_date - today).days
    return delta if delta >= 0 else None


def send_groupme_message(text):
    """Send a message to GroupMe."""
    bot_id = os.getenv("GROUPME_BOT_ID")
    if not bot_id:
        print("ERROR: GROUPME_BOT_ID not set")
        return False

    url = "https://api.groupme.com/v3/bots/post"
    try:
        while text:
            chunk = text[:1000]
            text = text[1000:]
            response = requests.post(url, json={"bot_id": bot_id, "text": chunk})
            if response.status_code != 201:
                print(f"Failed to send GroupMe message: {response.status_code}")
                return False
        return True
    except Exception as e:
        print(f"Error sending GroupMe message: {e}")
        return False


def check_and_notify():
    """Check calendar for events at 14, 7, and 3 day marks and send notifications."""
    init_db()  # Ensure database exists

    try:
        events = get_upcoming(days=14)
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return False

    notifications = {}  # Key: days_until, Value: list of (event_summary, event) tuples

    for event in events:
        tier = get_event_tier(event)
        if tier is None:
            continue  # Skip restricted events

        days = days_until_event(event)
        if days is None:
            continue

        # Check if event matches a notification tier
        should_notify = (tier == 1 and days == 14) or (tier == 2 and days == 7) or (tier == 3 and days == 3)

        if should_notify:
            # Only add if we haven't already sent this notification
            if not has_notification_been_sent(event["summary"], event["start"], tier, days):
                if days not in notifications:
                    notifications[days] = []
                notifications[days].append((event["summary"], event, tier))

    if not notifications:
        print("No new events to notify about.")
        return True

    # Build and send notification messages
    sent_count = 0
    for days_until in sorted(notifications.keys()):
        events_list = notifications[days_until]
        message = f"📅 Upcoming event(s) in {days_until} days:\n"

        for event_summary, event, tier in events_list:
            message += f"  • {event_summary}\n"

        print(f"Sending notification: {message}")
        if send_groupme_message(message.strip()):
            # Record each notification as sent
            for event_summary, event, tier in events_list:
                record_notification_sent(event_summary, event["start"], tier, days_until)
                sent_count += 1
        else:
            return False

    print(f"Successfully sent {sent_count} notifications.")

    # Clean up old records
    deleted = cleanup_old_notifications(days=30)
    print(f"Cleaned up {deleted} old notification records.")

    return True


if __name__ == "__main__":
    success = check_and_notify()
    sys.exit(0 if success else 1)
