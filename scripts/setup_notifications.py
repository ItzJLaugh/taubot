#!/usr/bin/env python3
"""
Setup script for automatic event notifications.
Initializes the notification tracking database and validates configuration.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.notification_tracker import init_db, cleanup_old_notifications
from src.services.calendar_service import get_upcoming, get_calendar_service
from dotenv import load_dotenv

load_dotenv()


def print_status(message, status="✓"):
    """Print a status message."""
    print(f"[{status}] {message}")


def check_environment():
    """Verify all required environment variables are set."""
    required_vars = {
        "GROUPME_BOT_ID": "GroupMe Bot ID",
        "OPENAI_API_KEY": "OpenAI API Key",
        "GOOGLE_CALENDAR_ID": "Google Calendar ID (optional, defaults to 'primary')",
    }

    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            if var == "GOOGLE_CALENDAR_ID":  # This one is optional
                continue
            missing.append(f"  • {var} ({description})")

    if missing:
        print("\n⚠ Missing environment variables:")
        for item in missing:
            print(item)
        print("\nAdd these to your .env file and try again.")
        return False

    print_status("All required environment variables are set")
    return True


def check_google_calendar():
    """Test Google Calendar connection."""
    try:
        service = get_calendar_service()
        events = get_upcoming(days=1)
        print_status(f"Google Calendar connected successfully ({len(events)} events found)")
        return True
    except Exception as e:
        print(f"✗ Google Calendar connection failed: {e}")
        return False


def initialize_database():
    """Initialize the notification tracking database."""
    try:
        init_db()
        print_status("Notification database initialized")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def cleanup_database():
    """Clean up old notification records."""
    try:
        deleted = cleanup_old_notifications(days=30)
        print_status(f"Database cleanup complete (removed {deleted} old records)")
        return True
    except Exception as e:
        print(f"✗ Database cleanup failed: {e}")
        return False


def main():
    """Run setup checks."""
    print("\n" + "="*50)
    print("TauBot Notification System Setup")
    print("="*50 + "\n")

    steps = [
        ("Checking environment variables", check_environment),
        ("Testing Google Calendar connection", check_google_calendar),
        ("Initializing notification database", initialize_database),
        ("Cleaning up old records", cleanup_database),
    ]

    results = []
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            success = step_func()
            results.append((step_name, success))
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results.append((step_name, False))

    print("\n" + "="*50)
    print("Setup Summary")
    print("="*50)

    all_success = True
    for step_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {step_name}")
        if not success:
            all_success = False

    if all_success:
        print("\n✓ All checks passed! Automatic notifications are ready.")
        print("\nNext steps:")
        print("  1. Start the Flask app: python src/app.py")
        print("  2. Check scheduler status: curl http://localhost:5000/scheduler/status")
        print("  3. Test notifications: curl -X POST http://localhost:5000/scheduler/check-now")
        print("\nFor more info, see AUTOMATIC_NOTIFICATIONS.md")
    else:
        print("\n✗ Setup failed. Please fix the issues above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
