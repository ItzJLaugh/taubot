"""Track which events have already been notified about to avoid duplicates."""

import os
import sqlite3
import datetime
from pathlib import Path

DB_FILE = os.getenv("NOTIFICATION_DB", "notification_tracker.db")


def init_db():
    """Initialize the notification tracking database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_summary TEXT NOT NULL,
            event_start TEXT NOT NULL,
            tier INTEGER NOT NULL,
            days_until INTEGER NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def has_notification_been_sent(event_summary, event_start, tier, days_until):
    """Check if we've already sent a notification for this event at this tier/day mark."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM sent_notifications
        WHERE event_summary = ? AND event_start = ? AND tier = ? AND days_until = ?
        LIMIT 1
    """, (event_summary, event_start, tier, days_until))

    result = cursor.fetchone()
    conn.close()

    return result is not None


def record_notification_sent(event_summary, event_start, tier, days_until):
    """Record that we sent a notification for this event."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sent_notifications (event_summary, event_start, tier, days_until)
        VALUES (?, ?, ?, ?)
    """, (event_summary, event_start, tier, days_until))

    conn.commit()
    conn.close()


def cleanup_old_notifications(days=30):
    """Clean up notification records older than specified days."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    cursor.execute("""
        DELETE FROM sent_notifications
        WHERE sent_at < ?
    """, (cutoff_date,))

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    return deleted
