from __future__ import annotations

from datetime import datetime
import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.scheduler.jobs import ChallengeSender

logger = logging.getLogger(__name__)


def create_scheduler(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Settings,
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    sender = ChallengeSender(bot=bot, session_factory=session_factory, settings=settings)

    scheduler.add_job(
        sender.send_due_challenges,
        trigger="interval",
        minutes=1,
        id="send_due_challenges",
        name="Send due Challenge Omid exercises",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
        next_run_time=datetime.now(settings.timezone_info),
    )
    return scheduler


def start_scheduler(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Settings,
) -> AsyncIOScheduler:
    scheduler = create_scheduler(bot=bot, session_factory=session_factory, settings=settings)
    scheduler.start()
    logger.info("APScheduler started", extra={"timezone": settings.timezone})
    return scheduler
