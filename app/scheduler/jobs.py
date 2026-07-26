from __future__ import annotations

from html import escape
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.database.models.challenge import Challenge
from app.database.repositories.challenge_repository import ChallengeRepository
from app.database.repositories.user_repository import UserRepository
from app.services.challenge_service import ChallengeService
from app.services.time import now_in_timezone

logger = logging.getLogger(__name__)


class ChallengeSender:
    def __init__(
        self,
        bot: Bot,
        session_factory: async_sessionmaker[AsyncSession],
        settings: Settings,
    ) -> None:
        self.bot = bot
        self.session_factory = session_factory
        self.settings = settings

    async def send_due_challenges(self) -> None:
        current_time = now_in_timezone(self.settings.timezone)
        async with self.session_factory() as session:
            challenge_repository = ChallengeRepository(session)
            user_repository = UserRepository(session)
            challenge_service = ChallengeService(
                challenges=challenge_repository,
                session=session,
                timezone_name=self.settings.timezone,
            )

            due_challenges = await challenge_service.get_due_challenges(current_time)
            if not due_challenges:
                logger.debug("No due challenges found")
                return

            active_users = await user_repository.list_active()
            if not active_users:
                logger.info("Due challenges found but no active users exist")

            for challenge in due_challenges:
                sent_count = 0
                failed_count = 0
                message_text = self._render_challenge(challenge)

                for user in active_users:
                    try:
                        await self.bot.send_message(chat_id=user.telegram_id, text=message_text)
                        sent_count += 1
                    except TelegramAPIError as exc:
                        failed_count += 1
                        logger.warning(
                            "Failed to send challenge to Telegram user",
                            extra={
                                "telegram_id": user.telegram_id,
                                "challenge_id": challenge.id,
                                "error": str(exc),
                            },
                        )

                await challenge_service.mark_sent(challenge, current_time)
                logger.info(
                    "Challenge delivery completed",
                    extra={
                        "challenge_id": challenge.id,
                        "day": challenge.day,
                        "sent_count": sent_count,
                        "failed_count": failed_count,
                    },
                )

    @staticmethod
    def _render_challenge(challenge: Challenge) -> str:
        return (
            f"🌟 <b>چالش امید - روز {challenge.day}</b>\n"
            f"<b>{escape(challenge.title)}</b>\n\n"
            f"{escape(challenge.description)}\n\n"
            "پاسخ خود را تا قبل از مهلت تعیین‌شده در همین گفتگو ارسال کنید."
        )
