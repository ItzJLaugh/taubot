# Credentials Quick Reference - Where to Find Everything

## At a Glance

| Variable | Where to Find | Looks Like | Time to Get |
|----------|---------------|-----------|------------|
| **GROUPME_BOT_ID** | GroupMe group settings → Bots | `abc123def456ghi789` | 2 min |
| **OPENAI_API_KEY** | https://platform.openai.com/account/api-keys | `sk-proj-abc123...xyz` | 2 min |
| **GOOGLE_CALENDAR_ID** | https://calendar.google.com → Calendar settings | `name@group.calendar.google.com` | 2 min |
| **GOOGLE_SERVICE_ACCOUNT_FILE** | Google Cloud Console (JSON file) | `credentials.json` in project folder | 10 min |

---

## 🤖 GROUPME_BOT_ID (2 minutes)

### Where:
1. Open GroupMe (https://web.groupme.com)
2. Click your fraternity group
3. Click group menu (⋯) → Settings/Details
4. Scroll to "Bots"
5. Click "Create Bot" or find existing bot
6. Copy the Bot ID

### Example:
```
GROUPME_BOT_ID=abc123def456ghi789jkl012mno345pqr
```

### What it looks like in GroupMe:
- Long alphanumeric string
- No spaces or special characters
- Usually 30+ characters long

---

## 🔑 OPENAI_API_KEY (2 minutes)

### Where:
1. Go to https://platform.openai.com/account/api-keys
2. Sign in (create account if needed: https://platform.openai.com/signup)
3. Click "+ Create new secret key"
4. Copy the key immediately (you can't see it again!)
5. Keep it somewhere safe

### Example:
```
OPENAI_API_KEY=sk-proj-abc123def456ghi789xyz...longstring...
```

### What it looks like:
- Starts with `sk-`
- Very long (100+ characters)
- After 2024, has "proj" in it: `sk-proj-...`

### Cost:
- Free tier available (small usage)
- Pay-as-you-go after free credits expire
- Check usage: https://platform.openai.com/account/billing/overview

---

## 📅 GOOGLE_CALENDAR_ID (2 minutes)

### Where:
1. Open Google Calendar (https://calendar.google.com)
2. Find your fraternity calendar in left sidebar
3. Right-click on calendar name → "Settings"
4. Scroll to "Integrate calendar" section
5. Copy the "Calendar ID"

### Example:
```
GOOGLE_CALENDAR_ID=your-chapter@group.calendar.google.com
```

OR if it's your personal calendar:
```
GOOGLE_CALENDAR_ID=primary
```

### What it looks like:
- If shared calendar: `name@group.calendar.google.com`
- If personal: `your-email@gmail.com` or `primary`

### If you don't have a shared calendar:
- Use `primary` (your personal calendar)
- Or create new calendar → Share with chapter members

---

## 🔐 GOOGLE_SERVICE_ACCOUNT_FILE (10 minutes)

This is the most complex. Follow carefully!

### Part 1: Create Google Cloud Project (2 min)

1. Go to https://console.cloud.google.com/
2. Click project dropdown at top
3. Click "New Project"
4. Name it: `TauBot` or `taubot-ai`
5. Click "Create"
6. Wait for project to be created

### Part 2: Enable Calendar API (2 min)

1. Click hamburger menu (☰) left sidebar
2. Click "APIs & Services" → "Library"
3. Search: `Google Calendar API`
4. Click result → "Enable"
5. (Optional) Search `Google Drive API` → "Enable"

### Part 3: Create Service Account & Key (5 min)

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: `taubot` or `taubot-service-account`
4. Click "Create and Continue"
5. Skip the roles, click "Continue"
6. Click on your new service account
7. Go to "Keys" tab
8. Click "Add Key" → "Create new key"
9. Select **JSON** format
10. Click "Create"
11. JSON file downloads automatically

### Part 4: Place credentials.json in your project

1. Find the downloaded JSON file (usually in Downloads)
2. Move/copy it to your project:
   ```
   c:\Users\jacks\OneDrive\Desktop\Python Environments\TauBot.ai\credentials.json
   ```

### Part 5: Share calendar with service account (1 min)

1. Get service account email:
   - Google Cloud → Credentials → Click your service account
   - Copy email (looks like: `taubot@taubot-ai.iam.gserviceaccount.com`)

2. Open Google Calendar
3. Right-click fraternity calendar → "Settings"
4. Scroll to "Share with specific people or groups"
5. Click "Add people and groups"
6. Paste service account email
7. Set permission: "See all event details"
8. Click "Send"

### What it looks like:
```
{
  "type": "service_account",
  "project_id": "taubot-ai",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "taubot@taubot-ai.iam.gserviceaccount.com",
  ...
}
```

### In .env file:
```
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json
```

---

## Complete .env File

Once you have all four values:

```env
# GroupMe Configuration
GROUPME_BOT_ID=abc123def456ghi789jkl012mno345pqr

# Google Cloud Configuration
GOOGLE_CALENDAR_ID=your-chapter@group.calendar.google.com
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-abc123def456ghi789xyz...longstring...
```

---

## Verify Everything Works

```bash
# Run setup verification
python scripts/setup_notifications.py
```

Expected output:
```
✓ All required environment variables are set
✓ Google Calendar connected successfully
✓ Notification database initialized
✓ Database cleanup complete
✓ All checks passed!
```

If you see errors, see the troubleshooting section below.

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| `GROUPME_BOT_ID not found` | Check bot exists in your group; verify ID copied correctly |
| `Google Calendar connection failed` | Enable Calendar API; share calendar with service account email |
| `credentials.json not found` | Make sure file is in project root; not in subdirectory |
| `OpenAI API key invalid` | Verify it starts with `sk-`; check entire key copied |
| `Permission denied` | Service account email not shared with calendar; re-share with "See all events" permission |

---

## Security Checklist

- ✓ Never commit `.env` to git (add to `.gitignore`)
- ✓ Never share `credentials.json` file
- ✓ Never post `OPENAI_API_KEY` or `GROUPME_BOT_ID` in chat/email
- ✓ If leaked, rotate the key immediately:
  - OpenAI: Delete key, create new one
  - GroupMe: Delete bot, create new one
  - Google: Delete service account key, create new one

---

## Estimated Timeline

| Step | Time |
|------|------|
| GroupMe Bot ID | 2 min |
| OpenAI API Key | 2 min |
| Google Calendar ID | 2 min |
| Google Service Account | 10 min |
| **Total** | **~15 minutes** |

---

## Still Stuck?

See the full guide: `CREDENTIALS_SETUP.md`

Or run this to diagnose issues:
```bash
python scripts/setup_notifications.py
```

It will tell you exactly what's missing or broken!
