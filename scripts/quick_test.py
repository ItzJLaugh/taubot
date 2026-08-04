#!/usr/bin/env python3
"""
Quick test script - run this to verify everything is working live.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.calendar_service import get_upcoming, get_calendar_service
from src.services.notification_tracker import init_db, cleanup_old_notifications
from dotenv import load_dotenv

load_dotenv()

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_pass(text):
    print(f"{GREEN}✓ PASS{RESET}: {text}")

def print_fail(text):
    print(f"{RED}✗ FAIL{RESET}: {text}")

def print_info(text):
    print(f"{YELLOW}ℹ INFO{RESET}: {text}")

def test_environment():
    """Test environment variables are set."""
    print_header("Test 1: Environment Variables")

    required = {
        'GROUPME_BOT_ID': 'GroupMe Bot ID',
        'OPENAI_API_KEY': 'OpenAI API Key',
    }

    optional = {
        'GOOGLE_CALENDAR_ID': 'Google Calendar ID (defaults to "primary")',
        'GOOGLE_SERVICE_ACCOUNT_FILE': 'Google Service Account File',
        'GOOGLE_SERVICE_ACCOUNT_JSON': 'Google Service Account JSON',
    }

    all_pass = True
    for var, desc in required.items():
        value = os.getenv(var)
        if value:
            print_pass(f"{desc} is set")
        else:
            print_fail(f"{desc} is NOT set - add to .env")
            all_pass = False

    print_info("Optional variables:")
    for var, desc in optional.items():
        value = os.getenv(var)
        if value:
            if len(value) > 40:
                print_info(f"  {desc}: {value[:40]}...")
            else:
                print_info(f"  {desc}: {value}")

    return all_pass

def test_calendar():
    """Test calendar connection."""
    print_header("Test 2: Google Calendar Connection")

    try:
        service = get_calendar_service()
        print_pass("Calendar service created")
    except Exception as e:
        print_fail(f"Calendar service failed: {e}")
        return False

    try:
        events = get_upcoming(days=1)
        print_pass(f"Calendar connection works - found {len(events)} events today")

        if events:
            print_info("Today's events:")
            for e in events[:3]:
                print_info(f"  • {e['summary']} at {e['start']}")
            if len(events) > 3:
                print_info(f"  ... and {len(events) - 3} more")
        else:
            print_info("No events found for today (that's OK)")

        return True
    except Exception as e:
        print_fail(f"Failed to fetch events: {e}")
        return False

def test_groupme():
    """Test GroupMe bot."""
    print_header("Test 3: GroupMe Bot Connection")

    bot_id = os.getenv('GROUPME_BOT_ID')
    if not bot_id:
        print_fail("GROUPME_BOT_ID not set")
        return False

    url = 'https://api.groupme.com/v3/bots/post'
    message = f'🤖 TauBot Test - {datetime.now().strftime("%H:%M:%S")}'

    try:
        response = requests.post(url, json={'bot_id': bot_id, 'text': message})

        if response.status_code == 201:
            print_pass("GroupMe bot is working")
            print_info("✅ CHECK GROUPME - test message should appear")
            return True
        else:
            print_fail(f"GroupMe returned status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_fail(f"Failed to reach GroupMe: {e}")
        return False

def test_database():
    """Test notification database."""
    print_header("Test 4: Notification Database")

    try:
        init_db()
        print_pass("Database initialized")
    except Exception as e:
        print_fail(f"Database initialization failed: {e}")
        return False

    try:
        import sqlite3
        conn = sqlite3.connect('notification_tracker.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sent_notifications")
        count = cursor.fetchone()[0]

        print_pass(f"Database contains {count} notification records")

        if count > 0:
            cursor.execute(
                "SELECT event_summary, tier, days_until, sent_at "
                "FROM sent_notifications ORDER BY sent_at DESC LIMIT 3"
            )
            print_info("Recent notifications:")
            for row in cursor.fetchall():
                print_info(f"  • {row[0]} (Tier {row[1]}, {row[2]} days) - {row[3]}")

        conn.close()
        return True
    except Exception as e:
        print_fail(f"Database query failed: {e}")
        return False

def test_scheduler():
    """Test scheduler via HTTP."""
    print_header("Test 5: Scheduler Status (via HTTP)")

    try:
        response = requests.get('http://localhost:5000/scheduler/status', timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data.get('running'):
                print_pass("Scheduler is running")

                jobs = data.get('jobs', [])
                print_info(f"Found {len(jobs)} scheduled jobs:")
                for job in jobs:
                    next_run = job.get('next_run_time', 'Unknown')
                    print_info(f"  • {job['name']} - Next: {next_run}")

                return True
            else:
                print_fail("Scheduler is NOT running")
                return False
        else:
            print_fail(f"Scheduler endpoint returned {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_fail("Cannot connect to app (is it running on port 5000?)")
        print_info("Start the app with: python src/app.py")
        return False
    except Exception as e:
        print_fail(f"Scheduler test failed: {e}")
        return False

def test_manual_trigger():
    """Test manual notification trigger."""
    print_header("Test 6: Manual Trigger")

    try:
        print_info("Triggering manual notification check...")
        response = requests.post('http://localhost:5000/scheduler/check-now', timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_pass("Manual check completed successfully")
                print_info("Check GroupMe for any announcements")
                return True
            else:
                print_fail(f"Manual check returned: {data.get('message', 'Unknown error')}")
                return False
        else:
            print_fail(f"Manual check returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_fail("Cannot connect to app (is it running on port 5000?)")
        return False
    except requests.exceptions.Timeout:
        print_fail("Manual check timed out (took > 10 seconds)")
        return False
    except Exception as e:
        print_fail(f"Manual trigger failed: {e}")
        return False

def main():
    print(f"{GREEN}")
    print("╔" + "="*58 + "╗")
    print("║" + "TauBot Notification System - Quick Test".center(58) + "║")
    print("╚" + "="*58 + "╝")
    print(f"{RESET}")

    results = []

    # Run all tests
    results.append(("Environment Variables", test_environment()))
    results.append(("Calendar Connection", test_calendar()))
    results.append(("GroupMe Bot", test_groupme()))
    results.append(("Database", test_database()))
    results.append(("Scheduler", test_scheduler()))
    results.append(("Manual Trigger", test_manual_trigger()))

    # Summary
    print_header("Test Summary")

    passes = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status}: {test_name}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"Results: {GREEN}{passes}/{total} tests passed{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    if passes == total:
        print(f"{GREEN}✓ All systems operational!{RESET}")
        print(f"{YELLOW}Things to verify:{RESET}")
        print(f"  1. Check GroupMe for test messages")
        print(f"  2. Create test calendar events")
        print(f"  3. Watch scheduler announce them")
        print(f"  4. Read TESTING_GUIDE.md for more scenarios")
        return 0
    else:
        print(f"{RED}✗ Some tests failed. Review above for details.{RESET}")
        print(f"{YELLOW}Common issues:{RESET}")
        print(f"  • App not running? Start with: python src/app.py")
        print(f"  • .env not set? Copy .env.example and add values")
        print(f"  • Calendar error? Run: python scripts/setup_notifications.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
