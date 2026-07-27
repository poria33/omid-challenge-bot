from aiogram import Bot, Dispatcher

from app.core.config import get_settings
from app.bot.routers import router
from app.scheduler.runner import start_scheduler


settings = get_settings()

bot = Bot(token=settings.bot_token)

dp = Dispatcher()

# ثبت handler ها
dp.include_router(router)


async def run_bot():
    print("Bot started...")

    await start_scheduler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_bot())