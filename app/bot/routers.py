from aiogram import Dispatcher

from app.bot.handlers import registration, submissions


def setup_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(registration.router)
    dispatcher.include_router(submissions.router)
