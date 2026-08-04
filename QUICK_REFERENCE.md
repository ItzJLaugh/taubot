# Quick Reference Card - Testing & Live Verification

## Start the System (Terminal 1)

```bash
cd c:\Users\jacks\OneDrive\Desktop\Python\ Environments\TauBot.ai
python src/app.py
```

**Expected output:**
```
✓ Background scheduler initialized for automatic event notifications
✓ Calendar connected successfully!
 * Running on http://127.0.0.1:5000
```

## Quick Test (Terminal 2)

### Test Everything at Once
```bash
python scripts/quick_test.py
```

This runs all 6 tests and tells you what's working/broken.

### Test Individual Components

**Scheduler Status:**
```bash
curl http://localhost:5000/scheduler/status
```
Should show `"running": true` and list jobs.

**Send Test Message to GroupMe:**
```bash
curl -X POST http://localhost:5000/scheduler/check-now
```
Check GroupMe for `📅 Upcoming event(s)...` message.

**Check Calendar Events:**
```bash
python -c "from src.services.calendar_service import get_upcoming; events = get_upcoming(); print(f'Found {len(events)} events'); [print(f'  • {e[\"summary\"]}') for e in events[:5]]"
```

**View Notifications Sent:**
```bash
sqlite3 notification_tracker.db "SELECT event_summary, tier, days_until FROM sent_notifications ORDER BY sent_at DESC LIMIT 5;"
```

**Send Direct GroupMe Message (for testing):**
```bash
python -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
bot_id = os.getenv('GROUPME_BOT_ID')
requests.post('https://api.groupme.com/v3/bots/post', json={'bot_id': bot_id, 'text': '✅ TauBot Test'})
print('Check GroupMe!')
"
```

## One-Minute Verification

1. **App running?**
   ```bash
   curl http://localhost:5000/  # Should return "TauBot is running!"
   ```

2. **Scheduler active?**
   ```bash
   curl http://localhost:5000/scheduler/status  # Should have "running": true
   ```

3. **Can send messages?**
   ```bash
   curl -X POST http://localhost:5000/scheduler/check-now  # Check GroupMe
   ```

## Common Commands

| What | Command |
|------|---------|
| Start app | `python src/app.py` |
| Test everything | `python scripts/quick_test.py` |
| Setup & verify | `python scripts/setup_notifications.py` |
| Trigger notification | `curl -X POST http://localhost:5000/scheduler/check-now` |
| Check scheduler | `curl http://localhost:5000/scheduler/status` |
| View database | `sqlite3 notification_tracker.db "SELECT * FROM sent_notifications;"` |
| Get events | `python scripts/calendar_notifier.py` |
| Reset database | `rm notification_tracker.db` |
| View app help | `python src/app.py --help` |

## Troubleshooting Quick Fixes

**Problem:** App won't start
```bash
# Install missing packages
pip install -r requirements.txt

# Check Python version (need 3.8+)
python --version
```

**Problem:** Scheduler not running
```bash
# Check APScheduler
python -c "import apscheduler; print('OK')"

# Restart app
python src/app.py
```

**Problem:** No GroupMe messages
```bash
# Verify bot ID
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROUPME_BOT_ID'))"

# Test bot directly
python -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
bot_id = os.getenv('GROUPME_BOT_ID')
r = requests.post('https://api.groupme.com/v3/bots/post', json={'bot_id': bot_id, 'text': 'Test'})
print(f'Status: {r.status_code}')
"
```

**Problem:** No calendar events found
```bash
# Test calendar connection
python -c "from src.services.calendar_service import get_upcoming; print(get_upcoming())"

# Run full setup check
python scripts/setup_notifications.py
```

**Problem:** Getting duplicate messages
```bash
# Delete database (will rebuild on next run)
rm notification_tracker.db

# Verify single worker (if deployed)
gunicorn -w 1 -b 0.0.0.0:5000 src.app:app
```

## Testing Workflow

### 1. Create Test Event
- Go to Google Calendar
- Create event titled "Test Formal Event" for tomorrow
- Add keyword like "formal" or "mandatory" to category it as Tier 1

### 2. Trigger Check
```bash
curl -X POST http://localhost:5000/scheduler/check-now
```

### 3. Verify Announcement
- Check GroupMe for message
- Should see: `📅 Upcoming event(s) in X days: • Test Formal Event`

### 4. Check Database
```bash
sqlite3 notification_tracker.db "SELECT * FROM sent_notifications WHERE event_summary LIKE '%Test%';"
```

### 5. Test No Duplicates
```bash
# Run check again
curl -X POST http://localhost:5000/scheduler/check-now

# Should NOT announce twice
```

### 6. Cleanup
```bash
# Delete test events from Google Calendar
# Delete from database:
sqlite3 notification_tracker.db "DELETE FROM sent_notifications WHERE event_summary LIKE '%Test%';"
```

## Understanding Tier System

- **Tier 1 (14 days):** Keywords like "mandatory", "brotherhood", "formal", "party", "rush"
- **Tier 2 (7 days):** Keywords like "philanthropy", "service", "dues", "volunteer"
- **Tier 3 (3 days):** Everything else
- **Restricted:** Events with "initiation" (never announced)

## Files You'll Reference

| When | Read |
|------|------|
| Want quick start | `NOTIFICATIONS_QUICK_START.md` |
| Testing/troubleshooting | `TESTING_GUIDE.md` (this file) |
| Customizing keywords | `NOTIFICATION_TIERS_GUIDE.md` |
| Full reference | `AUTOMATIC_NOTIFICATIONS.md` |
| Technical details | `IMPLEMENTATION_SUMMARY.md` |
| Production deployment | `DEPLOYMENT_CHECKLIST.md` |

## Live Monitoring

Watch notifications in real-time:

**Terminal 1: App logs**
```bash
python src/app.py
# Watch for: [check_and_notify] and [notifications sent]
```

**Terminal 2: Database changes**
```bash
while true; do
  sqlite3 notification_tracker.db "SELECT COUNT(*) FROM sent_notifications;"
  sleep 5
done
```

**Terminal 3: Test commands**
```bash
# Trigger checks
curl -X POST http://localhost:5000/scheduler/check-now
```

## Status Check (30 seconds)

```bash
#!/bin/bash
echo "=== TauBot Status ==="
echo "1. App running:"
curl -s http://localhost:5000/ || echo "NOT RUNNING"

echo -e "\n2. Scheduler status:"
curl -s http://localhost:5000/scheduler/status | jq '.running'

echo -e "\n3. Notifications in DB:"
sqlite3 notification_tracker.db "SELECT COUNT(*) FROM sent_notifications;"

echo -e "\n4. Latest notifications:"
sqlite3 notification_tracker.db "SELECT event_summary FROM sent_notifications ORDER BY sent_at DESC LIMIT 3;"
```

Save as `status.sh` and run: `bash status.sh`

## Deploying to Production

When you're ready to deploy:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** on your hosting platform

3. **Deploy with single worker:**
   ```bash
   gunicorn -w 1 -b 0.0.0.0:5000 src.app:app
   ```

4. **Test live:**
   ```bash
   curl -X POST https://your-domain.com/scheduler/check-now
   ```

## Customization Hints

**Change notification time:**
- Edit: `src/services/scheduler.py`
- Line: `CronTrigger(hour=9, minute=0)`
- Change `9` to your preferred hour (0-23)

**Add custom keywords:**
- Edit: `scripts/calendar_notifier.py`
- Find: `TIER_1_KEYWORDS`, `TIER_2_KEYWORDS`
- Add your keywords to the lists

**Adjust days before event:**
- Edit: `scripts/calendar_notifier.py`
- Find: `should_notify = (tier == 1 and days == 14)`
- Change `14` to different number

---

**Need help?** Run: `python scripts/quick_test.py` for automated diagnostics
