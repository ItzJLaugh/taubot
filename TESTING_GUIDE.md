# Testing Guide - Automatic Event Announcements

Complete guide to test and verify your automatic announcement system is live and working.

## Quick Test (2 minutes)

### Step 1: Start the App
```bash
python src/app.py
```

You should see:
```
✓ Background scheduler initialized for automatic event notifications
✓ Calendar connected successfully!
 * Running on http://127.0.0.1:5000
```

### Step 2: Check Scheduler is Running
```bash
curl http://localhost:5000/scheduler/status
```

Expected response:
```json
{
  "running": true,
  "jobs": [
    {
      "id": "daily_event_check",
      "name": "Daily event notification check",
      "next_run_time": "2026-08-04 09:00:00"
    },
    {
      "id": "periodic_event_check",
      "name": "Periodic event notification check (every 6 hours)",
      "next_run_time": "2026-08-03 18:00:00"
    }
  ]
}
```

**If you see this:** ✅ Scheduler is live and running!

### Step 3: Send Test Notification
```bash
curl -X POST http://localhost:5000/scheduler/check-now
```

Expected response:
```json
{
  "success": true,
  "message": "Manual check completed"
}
```

**Check GroupMe** → Should see a message like:
```
📅 Upcoming event(s) in X days:
  • Event Name
```

**If nothing appears in GroupMe:**
- Check Step 4 below (Troubleshoot)
- Verify your `GROUPME_BOT_ID` is correct

---

## Complete Testing Workflow

### Test 1: Verify Calendar Connection

```bash
python -c "
from src.services.calendar_service import get_upcoming
events = get_upcoming()
print(f'Found {len(events)} upcoming events')
for e in events[:3]:
    print(f'  • {e[\"summary\"]} - {e[\"start\"]}')
"
```

**Expected:** Shows your calendar events

**If fails:** Calendar credentials issue
```bash
# Run setup to diagnose
python scripts/setup_notifications.py
```

### Test 2: Verify GroupMe Bot Works

```bash
python -c "
import requests
import os
from dotenv import load_dotenv

load_dotenv()
bot_id = os.getenv('GROUPME_BOT_ID')
url = 'https://api.groupme.com/v3/bots/post'
response = requests.post(url, json={'bot_id': bot_id, 'text': '✅ TauBot Test Message'})
print(f'Status: {response.status_code}')
print('Check GroupMe for the test message!')
"
```

**Expected:** Status 201, message appears in GroupMe

**If fails:**
- GroupMe bot ID is wrong
- GroupMe API is down
- Network issue

### Test 3: Check Notification Database

```bash
sqlite3 notification_tracker.db "SELECT * FROM sent_notifications ORDER BY sent_at DESC LIMIT 5;"
```

**Expected:** Shows recent notifications sent

**If empty:** Either no events matched tiers, or first time running

### Test 4: View Notification Details

```bash
sqlite3 notification_tracker.db "
SELECT 
    event_summary,
    tier,
    days_until,
    sent_at
FROM sent_notifications 
ORDER BY sent_at DESC 
LIMIT 10;
"
```

This shows what was announced when.

### Test 5: Verify Tier Categorization

Create a test calendar event with title "Test Formal Event" and run:

```bash
python -c "
from src.services.calendar_service import get_upcoming
from scripts.calendar_notifier import get_event_tier

events = get_upcoming()
for e in events:
    if 'Test' in e['summary']:
        tier = get_event_tier(e)
        print(f'Event: {e[\"summary\"]}')
        print(f'Tier: {tier}')
        print(f'Start: {e[\"start\"]}')
"
```

**Expected:** Shows the tier (1, 2, or 3) assigned to your test event

---

## Scenario Testing

### Scenario 1: Test Immediate Notification

Create a test event **tomorrow** with title "Test Formal Event":

```bash
# Trigger check
curl -X POST http://localhost:5000/scheduler/check-now

# Check GroupMe - should announce "in 1 days"
```

### Scenario 2: Test No Duplicate Notifications

Run the check twice:

```bash
curl -X POST http://localhost:5000/scheduler/check-now
# Wait 2 seconds
curl -X POST http://localhost:5000/scheduler/check-now
```

**Expected:** GroupMe only shows message once

Check database:
```bash
sqlite3 notification_tracker.db "
SELECT COUNT(*) as duplicate_count 
FROM sent_notifications 
WHERE event_summary = 'Test Formal Event';
"
```

**Expected:** Count is 1 (not 2)

### Scenario 3: Test Different Tiers

Create three test events:

**Event 1: "Test Mandatory Meeting"**
- Tomorrow
- Should trigger Tier 1 (announces immediately as "in 1 days")

**Event 2: "Test Service Project"**
- In 7 days
- Should trigger Tier 2 (wait, or adjust timing)

**Event 3: "Test Regular Meeting"**
- In 3 days
- Should trigger Tier 3

Run check:
```bash
curl -X POST http://localhost:5000/scheduler/check-now
```

Check GroupMe - should see all three announcements.

### Scenario 4: Test Restricted Keywords

Create event: "Test Initiation Ceremony" and run check:

```bash
curl -X POST http://localhost:5000/scheduler/check-now
```

**Expected:** Event NOT announced (nothing in GroupMe for this event)

Verify in database:
```bash
sqlite3 notification_tracker.db "
SELECT * FROM sent_notifications 
WHERE event_summary LIKE '%Initiation%';
"
```

**Expected:** Empty (no results)

---

## Live Polling Verification

### Verify Scheduler Runs Automatically

1. Note current time: `date`
2. Change scheduler to run in 2 minutes (for testing):

```python
# Edit src/services/scheduler.py
# Change: CronTrigger(hour=9, minute=0)
# To: CronTrigger(hour=CURRENT_HOUR, minute=CURRENT_MINUTE+2)
# Example: if it's 3:45 PM, use minute=47
```

3. Restart app: `python src/app.py`
4. Create test event for tomorrow: "Test Auto Announce"
5. Wait for scheduled time to pass
6. Check GroupMe - should see announcement automatically

**If it announces automatically:** ✅ Polling is working!

### Monitor Scheduler Activity

Keep this running while app is active:

```bash
while true; do
  curl -s http://localhost:5000/scheduler/status | jq '.jobs[0].next_run_time'
  sleep 5
done
```

This shows when the next check is scheduled.

### Monitor Logs in Real Time

```bash
# In a separate terminal
tail -f /path/to/app/output.log
```

Or if running in foreground, watch the console output for:
- `check_and_notify()` running
- Events found
- Notifications sent

---

## Troubleshooting Tests

### Problem: Scheduler Status Shows `"running": false`

```bash
# Check for errors in app startup
python src/app.py 2>&1 | grep -i "error\|warning"

# Verify APScheduler installed
python -c "import apscheduler; print('✓ APScheduler OK')"

# Try importing scheduler
python -c "from src.services.scheduler import init_scheduler; print('✓ Scheduler imports OK')"
```

### Problem: No GroupMe Message Appears

**Test 1: GroupMe bot ID**
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
bot_id = os.getenv('GROUPME_BOT_ID')
print(f'Bot ID: {bot_id}')
print('If empty, add to .env!')
"
```

**Test 2: GroupMe API directly**
```bash
python -c "
import requests
import os
from dotenv import load_dotenv

load_dotenv()
bot_id = os.getenv('GROUPME_BOT_ID')
url = 'https://api.groupme.com/v3/bots/post'
r = requests.post(url, json={'bot_id': bot_id, 'text': 'Direct test'})
print(f'Status: {r.status_code}')
if r.status_code == 201:
    print('✓ GroupMe working!')
else:
    print(f'✗ Error: {r.text}')
"
```

**Test 3: Notification script directly**
```bash
python scripts/calendar_notifier.py
```

Watch output for:
- Events found
- Notifications sent
- Any errors

### Problem: Calendar Connection Fails

```bash
# Run setup to diagnose
python scripts/setup_notifications.py

# Or test directly
python -c "
from src.services.calendar_service import get_calendar_service, get_upcoming
try:
    service = get_calendar_service()
    print('✓ Calendar service created')
    events = get_upcoming(days=1)
    print(f'✓ Found {len(events)} events today')
except Exception as e:
    print(f'✗ Error: {e}')
"
```

### Problem: Getting Duplicate Notifications

```bash
# Delete database to reset
rm notification_tracker.db

# Verify single worker (if deployed)
# Check: gunicorn -w 1 ...
# If using -w 4 or more, reduce to -w 1

# Restart app
python src/app.py
```

### Problem: Database Locked Error

```bash
# Check for multiple app instances
ps aux | grep "python src/app.py"

# Kill duplicates if found
kill -9 <PID>

# Restart once
python src/app.py
```

---

## Testing Checklist

### Basic Functionality ✓
- [ ] App starts without errors
- [ ] Scheduler initializes successfully
- [ ] `/scheduler/status` returns running=true
- [ ] Manual check (`/scheduler/check-now`) succeeds

### Calendar & Events ✓
- [ ] Calendar connection works
- [ ] Can fetch upcoming events
- [ ] Test event appears in calendar
- [ ] Event correctly categorized by tier

### GroupMe Integration ✓
- [ ] Test message sends to GroupMe
- [ ] Message format is correct
- [ ] No message characters cut off (1000 char limit)

### Automatic Scheduling ✓
- [ ] Scheduler runs at configured time
- [ ] Scheduler runs every 6 hours
- [ ] Announcement sent automatically (not manual)

### Duplicate Prevention ✓
- [ ] Database tracks notifications
- [ ] Same event not announced twice
- [ ] Old records cleaned up after 30 days

### Tier System ✓
- [ ] Tier 1 events announce at 14 days
- [ ] Tier 2 events announce at 7 days
- [ ] Tier 3 events announce at 3 days
- [ ] Restricted events never announced

---

## Performance Testing

### Check Message Throughput

Create 10 test events and trigger check:

```bash
curl -X POST http://localhost:5000/scheduler/check-now
```

**Expected:**
- All events processed
- All announcements sent within seconds
- Database records updated

### Monitor Memory Usage

```bash
# Before check
ps aux | grep python | grep app

# Note memory usage, run check, check again
curl -X POST http://localhost:5000/scheduler/check-now

# Memory should be similar (no leaks)
```

### Check Response Times

```bash
time curl -X POST http://localhost:5000/scheduler/check-now
```

**Expected:** Completes in < 5 seconds

---

## Cleanup After Testing

Delete test events from Google Calendar:
```bash
# Go to calendar, delete events with "Test" in name
```

Clean test notifications from database:
```bash
sqlite3 notification_tracker.db "
DELETE FROM sent_notifications 
WHERE event_summary LIKE '%Test%';
"
```

Reset to production configuration:
```python
# In src/services/scheduler.py, restore:
# CronTrigger(hour=9, minute=0)  # Back to 9 AM
```

---

## Final Verification

Run this complete test to verify everything:

```bash
#!/bin/bash

echo "Testing TauBot Notification System..."
echo ""

echo "1. Checking scheduler status..."
curl -s http://localhost:5000/scheduler/status | jq .

echo ""
echo "2. Running manual check..."
curl -s -X POST http://localhost:5000/scheduler/check-now | jq .

echo ""
echo "3. Checking database..."
sqlite3 notification_tracker.db "SELECT COUNT(*) as total_notifications FROM sent_notifications;"

echo ""
echo "✓ System is live and running!"
```

Save as `test_system.sh` and run:
```bash
bash test_system.sh
```

---

## Summary

Your system is working if:

✅ Scheduler shows running=true  
✅ Manual check completes successfully  
✅ Test message appears in GroupMe  
✅ Database records notifications  
✅ No duplicate messages  
✅ Automatic checks run on schedule  

If all are true: **You're ready for production!**
