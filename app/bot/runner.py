from aiogram import Bot, Dispatcher

from app.core.config import get_settings


settings = get_settings()

bot = Bot(token=settings.bot_token)

dp = Dispatcher()


async def run_bot():
    from app.scheduler.runner import start_scheduler

    start_scheduler()

    await dp.start_polling(bot)