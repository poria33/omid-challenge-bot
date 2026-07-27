from aiogram import Bot, Dispatcher

from app.core.config import get_settings
from app.bot.routers import setup_routers


settings = get_settings()

bot = Bot(token=settings.bot_token)

dp = Dispatcher()

setup_routers(dp)


async def run_bot():
    from app.scheduler.runner import start_scheduler

    start_scheduler()

    print("Bot started...")

    await dp.start_polling(bot)