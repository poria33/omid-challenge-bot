from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.jobs import send_due_challenges
from app.core.logger import logger


scheduler = AsyncIOScheduler()


def start_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(
        send_due_challenges,
        trigger="interval",
        minutes=1,
        id="send_due_challenges",
        replace_existing=True,
        name="Send due Challenge Omid exercises",
    )

    scheduler.start()

    logger.info(
        "APScheduler started"
    )