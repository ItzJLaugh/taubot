# Notification Tiers Guide

This guide helps you understand and customize the automatic notification system.

## Quick Reference

| Tier | Days Before | Urgency | Examples | Keywords |
|------|-------------|---------|----------|----------|
| 1 | 14 | CRITICAL | Rush events, Formals, Mandatory | `mandatory`, `brotherhood`, `formal`, `semi`, `party`, `rush`, `alumni` |
| 2 | 7 | HIGH | Service projects, Dues | `philanthropy`, `service`, `dues`, `volunteer`, `community` |
| 3 | 3 | NORMAL | Regular meetings, Socials | (all other events) |
| ❌ | NEVER | SECRET | Initiation, Private events | `initiation`, `initiate`, `initiated`, `initiating` |

## Timeline Example

Imagine an event: "Fall Formal - October 15th"

```
September 17 (28 days before)
  └─ No notification yet

September 30 (14 days before) - TIER 1 TRIGGERED ✅
  └─ GroupMe: "📅 Upcoming event(s) in 14 days:
              • Fall Formal - October 15th"

October 8 (7 days before)
  └─ No notification (Tier 2 doesn't apply to "Formal" events)

October 12 (3 days before)
  └─ No notification (Tier 3 doesn't apply to "Formal" events)

October 15
  └─ Event happens!
```

Another example: "Chapter Dues Collection - October 15th"

```
September 17 (28 days before)
  └─ No notification yet

September 30 (14 days before)
  └─ No notification (Tier 1 doesn't apply to "Dues")

October 8 (7 days before) - TIER 2 TRIGGERED ✅
  └─ GroupMe: "📅 Upcoming event(s) in 7 days:
              • Chapter Dues Collection - October 15th"

October 12 (3 days before)
  └─ No notification (already notified at Tier 2)

October 15
  └─ Event happens!
```

## How Keywords Work

The system looks for keywords in three places:
1. **Event title** (most important)
2. **Event description**
3. **Event location**

```
Event Details Example:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title:       "Fall Formal - Dinner & Dancing"
Description: "Brothers and pledges dress in formal attire"
Location:    "Ballroom at Downtown Hilton"
Time:        October 15, 2024 7:00 PM - Midnight
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System searches: "fall formal dinner dancing brothers pledges 
                 dress in formal attire ballroom at downtown hilton"

Found keyword "formal" → Tier 1 → Notify 14 days before
```

## Customizing for Your Chapter

### Step 1: Identify Your Events

Make a list of your chapter's regular events:
- Mandatory meetings?
- Service/philanthropy projects?
- Social events?
- Fundraisers?
- Alumni events?

### Step 2: Group by Urgency

**TIER 1 (Should know 2+ weeks ahead):**
- Events that are mandatory or formal
- Events that require planning/preparation
- High visibility events
- Alumni events

**TIER 2 (Should know 1 week ahead):**
- Volunteer/service opportunities
- Financial obligations (dues, fees)
- Community involvement
- Projects needing sign-ups

**TIER 3 (Should know 3 days ahead):**
- Regular chapter meetings
- Casual hangouts
- Study sessions
- Day-to-day activities

**Restricted (Never announce):**
- Initiation events
- Secret ceremonies
- Private meetings

### Step 3: Add Keywords

Edit `scripts/calendar_notifier.py`:

```python
# Add your chapter-specific keywords

TIER_1_KEYWORDS = [
    "mandatory", "brotherhood", "formal", "semi", 
    "party", "rush", "alumni",
    # Add YOUR keywords below:
    "officer meeting",      # If this is mandatory
    "pledge class meeting",  # If this is mandatory
    "fundraiser",          # Important event
    "banquet",             # Formal gathering
]

TIER_2_KEYWORDS = [
    "philanthropy", "service", "dues", "volunteer", "community",
    # Add YOUR keywords below:
    "donation",            # Money-related
    "gift",                # Money-related
    "building project",    # Service-related
    "cleanup",             # Service-related
]

TIER_3_KEYWORDS = [
    # Usually empty (catches everything else)
    # Add specific keywords only if you have very common events
]
```

### Step 4: Test Your Configuration

Create a test event in Google Calendar:
```
Title: "Test Formal Planning"
Description: "Planning committee for Fall Formal"
When: Tomorrow
```

Wait 1 minute, then trigger:
```bash
curl -X POST http://localhost:5000/scheduler/check-now
```

Should announce "in 1 days" or similar (depending on exact timing).

Delete the test event and notification from your database:
```bash
# See all notifications
sqlite3 notification_tracker.db "SELECT * FROM sent_notifications;"

# Delete test notification
sqlite3 notification_tracker.db "DELETE FROM sent_notifications WHERE event_summary LIKE '%Test%';"
```

## Common Customization Examples

### Adding "Movie Night" as Tier 3

```python
# Just name it "Movie Night" in calendar
# It will automatically be Tier 3 (catches all non-matching events)
```

### Adding "Fundraiser" as Tier 1 (Very Important)

```python
TIER_1_KEYWORDS = [
    "mandatory", "brotherhood", "formal", "semi", 
    "party", "rush", "alumni",
    "fundraiser"  # Add this line
]
```

### Making Dues Collection Critical (Tier 1 instead of 2)

```python
# Remove "dues" from Tier 2
TIER_2_KEYWORDS = [
    "philanthropy", "service", "volunteer", "community"
    # Remove: "dues"
]

# Add to Tier 1
TIER_1_KEYWORDS = [
    "mandatory", "brotherhood", "formal", "semi", 
    "party", "rush", "alumni",
    "dues"  # Add this line
]
```

### Announcing Events Sooner

If you want all events announced 1 week in advance instead of varied:

```python
# In calendar_notifier.py, change the timing logic:
should_notify = (tier == 1 and days == 7) or \
                (tier == 2 and days == 7) or \
                (tier == 3 and days == 7)

# All tiers now announce at 7 days
```

### Adding Timezone-Specific Announcement Time

```python
# In scheduler.py:
scheduler.add_job(
    check_and_notify,
    CronTrigger(hour=9, minute=0, timezone='America/Chicago'),
    # Specify your timezone: America/Chicago, America/New_York, etc.
)
```

## Testing Different Tiers

### Create Test Events

```
Tomorrow:        Create "Test Rush Event" → Should announce immediately
In 7 days:       Create "Test Philanthropy Event" → Should announce immediately
In 14 days:      Create "Test Formal Event" → Should announce immediately
In 5 days:       Create "Test Regular Meeting" → Wait 2 days to announce
```

Run: `curl -X POST http://localhost:5000/scheduler/check-now`

Each test event in its tier window should announce immediately.

## Notification Message Format

The system sends messages like:

```
📅 Upcoming event(s) in 14 days:
  • Fall Formal - October 15th

📅 Upcoming event(s) in 7 days:
  • Service Project - Habitat for Humanity

📅 Upcoming event(s) in 3 days:
  • Chapter Meeting - Thursday 7 PM
```

### Enhancing Messages with Event Details

To include time and location in announcements, edit `scripts/calendar_notifier.py`:

```python
# Current (simple):
message += f"  • {event_summary}\n"

# Enhanced (with details):
message += f"  • {event_summary}\n"
if event.get("start"):
    message += f"    When: {event['start']}\n"
if event.get("location"):
    message += f"    Where: {event['location']}\n"
```

Result:
```
📅 Upcoming event(s) in 14 days:
  • Fall Formal - October 15th
    When: 2024-10-15T19:00:00-05:00
    Where: Ballroom at Downtown Hilton
```

## Handling Conflicts

If an event has multiple matching keywords, **the highest tier wins**:

```
Event: "Mandatory Brotherhood Formal"
  - Contains: "mandatory" (Tier 1) ✓ WINS
  - Contains: "brotherhood" (Tier 1)
  - Result: Announced at Tier 1 (14 days)
```

```
Event: "Service Party for Dues Collection"
  - Contains: "service" (Tier 2)
  - Contains: "dues" (Tier 2)
  - Contains: "party" (Tier 1) ✓ WINS
  - Result: Announced at Tier 1 (14 days)
```

If you want to prevent this, use more specific keywords:
```python
TIER_2_KEYWORDS = [
    "philanthropy event",  # More specific than just "service"
    "service project",     # More specific than just "service"
]
```

## Restricted Keywords (Never Announce)

These are **protected** - events won't be announced even if they match Tier keywords:

```python
RESTRICTED_KEYWORDS = ["initiation", "initiate", "initiated", "initiating"]
```

If you have other sensitive topics, add them:
```python
RESTRICTED_KEYWORDS = [
    "initiation", "initiate", "initiated", "initiating",
    "officer election",    # If you want this private
    "disciplinary",        # If you want this private
]
```

## Verifying Your Changes

After editing `scripts/calendar_notifier.py`:

```bash
# Test syntax
python -m py_compile scripts/calendar_notifier.py

# Run a manual check
python scripts/calendar_notifier.py

# Watch logs
curl http://localhost:5000/scheduler/status
```

---

**Need help?** Run the setup script again: `python scripts/setup_notifications.py`
