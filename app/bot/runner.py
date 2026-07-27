from __future__ import annotations

import asyncio

from aiogram import Dispatcher, Bot

from app.core.config import get_settings
from app.bot.routers import setup_routers
from app.scheduler.runner import start_scheduler


settings = get_settings()

bot = Bot(
    token=settings.bot_token
)

dp = Dispatcher()


def setup_bot():

    setup_routers(dp)


async def run_bot():

    setup_bot()

    start_scheduler()

    print("Challenge Omid bot polling started")

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types()
    )


def main():

    asyncio.run(
        run_bot()
    )


if __name__ == "__main__":
    main()