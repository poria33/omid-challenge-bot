from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.middlewares.services import ServiceMiddleware
from app.bot.routers import setup_routers
from app.core.config import get_settings
from app.core.logger import setup_logging
from app.database.session import async_session_factory, close_db, init_models
from app.scheduler.runner import start_scheduler

logger = logging.getLogger(__name__)


async def run_bot() -> None:
    setup_logging()
    settings = get_settings()
    settings.validate_bot_runtime()

    if settings.auto_create_db:
        await init_models()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.update.outer_middleware(ServiceMiddleware(async_session_factory, settings))
    setup_routers(dispatcher)

    scheduler = start_scheduler(bot=bot, session_factory=async_session_factory, settings=settings)
    logger.info("Challenge Omid bot polling started")

    try:
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await bot.session.close()
        await close_db()
        logger.info("Challenge Omid bot polling stopped")


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
