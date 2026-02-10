"""Google Calendar service for fetching fraternity events."""

import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar_service():
    """Build and return a Google Calendar API service using a service account."""
    # On Render/cloud: load credentials from env var containing the JSON content
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if creds_json:
        info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )
        return build("calendar", "v3", credentials=credentials)

    # Locally: load credentials from file path
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not creds_path:
        raise ValueError("Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE")

    if not os.path.isabs(creds_path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        creds_path = os.path.join(project_root, creds_path)

    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=credentials)

def get_upcoming(days=40):
    """Fetch upcoming events from the Google Calendar.

    Args:
        days: Number of days ahead to look for events (default 40).

    Returns:
        A list of event dicts with 'summary', 'start', 'end', and 'location'.
    """
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    service = get_calendar_service()

    now = datetime.datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + datetime.timedelta(days=days)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    parsed = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        parsed.append({
            "summary": event.get("summary", "No title"),
            "start": start,
            "end": end,
            "location": event.get("location", ""),
            "description": event.get("description", ""),
        })

    return parsed


def format_events_for_context(events):
    """Format a list of events into a string the AI can use as context."""
    if not events:
        return "There are no upcoming events on the calendar."

    lines = ["Here are the upcoming events from the fraternity calendar:\n"]
    for e in events:
        line = f"- {e['summary']} | Start: {e['start']} | End: {e['end']}"
        if e["location"]:
            line += f" | Location: {e['location']}"
        if e["description"]:
            line += f" | Details: {e['description']}"
        lines.append(line)

    return "\n".join(lines)
