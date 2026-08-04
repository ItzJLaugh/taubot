"""Background scheduler for automatic event notifications."""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.calendar_notifier import check_and_notify

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def init_scheduler():
    """Initialize and start the background scheduler."""
    global scheduler

    if scheduler is not None:
        return scheduler

    scheduler = BackgroundScheduler()

    # Run check_and_notify every day at 9:00 AM
    # Adjust the hour/minute to match your preferred notification time
    scheduler.add_job(
        check_and_notify,
        CronTrigger(hour=9, minute=0),
        id='daily_event_check',
        name='Daily event notification check',
        replace_existing=True,
        misfire_grace_time=300,  # Wait up to 5 minutes if server was down
    )

    # Also run every 6 hours as a safety check
    # This ensures notifications go out even if the 9 AM check fails
    scheduler.add_job(
        check_and_notify,
        CronTrigger(hour='*/6'),
        id='periodic_event_check',
        name='Periodic event notification check (every 6 hours)',
        replace_existing=True,
        misfire_grace_time=300,
    )

    scheduler.start()
    logger.info("Scheduler initialized and started")

    return scheduler


def shutdown_scheduler():
    """Gracefully shut down the scheduler."""
    global scheduler

    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler shut down")


def get_scheduler_status():
    """Get current scheduler status and upcoming jobs."""
    global scheduler

    if scheduler is None:
        return {"running": False, "jobs": []}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time),
        })

    return {
        "running": scheduler.running,
        "jobs": jobs,
    }
