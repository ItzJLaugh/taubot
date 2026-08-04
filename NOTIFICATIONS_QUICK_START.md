# 🎉 Automatic Event Notifications - Quick Start

Your TauBot.ai is now set up to automatically announce upcoming events in the GroupMe chat!

## In 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Your Environment
Copy your configuration to `.env`:
```bash
cp .env.example .env
# Edit .env with your actual values:
# - GROUPME_BOT_ID
# - GOOGLE_CALENDAR_ID
# - OPENAI_API_KEY
```

### 3. Run the Setup Script
```bash
python scripts/setup_notifications.py
```

This will:
- ✓ Verify all environment variables
- ✓ Test Google Calendar connection
- ✓ Initialize the notification database
- ✓ Clean up any old records

## Start the Bot

```bash
python src/app.py
```

You should see:
```
✓ Background scheduler initialized for automatic event notifications
✓ Calendar connected successfully!
* Running on http://127.0.0.1:5000
```

## How It Works

The system will automatically:

1. **Check your calendar daily at 9:00 AM** (and every 6 hours as backup)
2. **Categorize events by importance** based on keywords in the event name/description
3. **Send announcements to GroupMe** at the right time:
   - **Tier 1** (Very Important): 14 days before
   - **Tier 2** (Important): 7 days before  
   - **Tier 3** (Regular): 3 days before

## Test It Immediately

```bash
# Trigger a manual check (for testing)
curl -X POST http://localhost:5000/scheduler/check-now

# Check scheduler status
curl http://localhost:5000/scheduler/status
```

## Customize for Your Chapter

### Add Custom Keywords

Events will be announced at different times based on keywords. Edit `scripts/calendar_notifier.py`:

```python
TIER_1_KEYWORDS = ["mandatory", "brotherhood", "formal", "semi", "party", "rush", "alumni"]
TIER_2_KEYWORDS = ["philanthropy", "service", "dues", "volunteer", "community"]
```

Add keywords your chapter uses! For example:
- Add `"fundraiser"` to TIER_2_KEYWORDS
- Add `"movie night"` to TIER_3_KEYWORDS

### Change Notification Times

Edit `src/services/scheduler.py` to change when notifications are sent:

```python
# Change 9:00 AM to another time (24-hour format)
CronTrigger(hour=9, minute=0)  # Change these numbers
```

## Production Deployment

When deploying to Render, Heroku, etc.:

1. **Use 1 worker only** (prevents duplicate notifications):
   ```bash
   gunicorn -w 1 -b 0.0.0.0:5000 src.app:app
   ```

2. **Set environment variables** in your cloud provider's dashboard

3. **Database persists automatically** in `notification_tracker.db`

## Troubleshooting

### No notifications sending?

1. Check scheduler is running:
   ```bash
   curl http://localhost:5000/scheduler/status
   ```

2. Check GroupMe bot ID is correct:
   ```bash
   python scripts/calendar_notifier.py
   ```

3. Verify Google Calendar connection:
   ```bash
   python -c "from src.services.calendar_service import get_upcoming; print(get_upcoming())"
   ```

### Keep seeing duplicate notifications?

Delete the database and it will rebuild:
```bash
rm notification_tracker.db
```

## Database Info

- Location: `notification_tracker.db` (SQLite, no special setup needed)
- Auto-cleanup: Old records deleted after 30 days
- View records: `sqlite3 notification_tracker.db "SELECT * FROM sent_notifications;"`

## What Gets Announced

The system announces events from your Google Calendar that:
- ✓ Are not marked as "initiation" related (protected)
- ✓ Have descriptive names/keywords
- ✓ Haven't already been announced for this tier/timeframe

## Next Steps

1. **Add your keywords** for events specific to your chapter
2. **Test with a calendar event** - add "test event" to calendar for tomorrow
3. **Adjust timing** if 9 AM doesn't work for your members
4. **Deploy to production** when you're confident

## Learn More

See [AUTOMATIC_NOTIFICATIONS.md](AUTOMATIC_NOTIFICATIONS.md) for advanced configuration.

---

Questions? Check the logs or run the setup script again: `python scripts/setup_notifications.py`
