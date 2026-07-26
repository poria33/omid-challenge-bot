from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.database.repositories.challenge_repository import ChallengeRepository
from app.database.repositories.submission_repository import SubmissionRepository
from app.database.repositories.user_repository import UserRepository
from app.services.challenge_service import ChallengeService
from app.services.registration_service import RegistrationService
from app.services.submission_service import SubmissionService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], settings: Settings) -> None:
        self.session_factory = session_factory
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            users = UserRepository(session)
            challenges = ChallengeRepository(session)
            submissions = SubmissionRepository(session)

            data["registration_service"] = RegistrationService(
                users=users,
                session=session,
                max_users=self.settings.max_users,
            )
            data["challenge_service"] = ChallengeService(
                challenges=challenges,
                session=session,
                timezone_name=self.settings.timezone,
            )
            data["submission_service"] = SubmissionService(
                users=users,
                challenges=challenges,
                submissions=submissions,
                session=session,
                timezone_name=self.settings.timezone,
            )
            data["settings"] = self.settings

            try:
                return await handler(event, data)
            except Exception:
                await session.rollback()
                raise
