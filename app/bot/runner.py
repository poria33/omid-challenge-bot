from aiogram import Bot, Dispatcher

from app.core.config import get_settings


settings = get_settings()

bot = Bot(token=settings.bot_token)

dp = Dispatcher()


def register_routers():
    from app.bot.handlers.registration import router as registration_router
    from app.bot.handlers.submissions import router as submissions_router

    dp.include_router(registration_router)
    dp.include_router(submissions_router)


async def run_bot():

    register_routers()

    from app.scheduler.runner import start_scheduler

    start_scheduler()

    print("Bot started...")

    await dp.start_polling(bot)