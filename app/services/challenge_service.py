from __future__ import annotations

from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.challenge import Challenge
from app.database.repositories.challenge_repository import ChallengeRepository
from app.services.exceptions import ValidationError
from app.services.time import day_window, now_in_timezone

logger = logging.getLogger(__name__)


class ChallengeService:
    def __init__(self, challenges: ChallengeRepository, session: AsyncSession, timezone_name: str) -> None:
        self.challenges = challenges
        self.session = session
        self.timezone_name = timezone_name

    async def create_challenge(
        self,
        day: int,
        title: str,
        description: str,
        send_time: datetime,
        deadline: datetime,
        is_active: bool = True,
    ) -> Challenge:
        if day < 1:
            raise ValidationError("Challenge day must be greater than zero.")
        if deadline <= send_time:
            raise ValidationError("Challenge deadline must be after send time.")

        existing = await self.challenges.get_by_day(day)
        if existing:
            raise ValidationError(f"Challenge day {day} already exists.")

        challenge = await self.challenges.create_challenge(
            day=day,
            title=title.strip(),
            description=description.strip(),
            send_time=send_time,
            deadline=deadline,
            is_active=is_active,
        )
        await self.session.commit()
        await self.challenges.refresh(challenge)
        logger.info("Created challenge", extra={"challenge_id": challenge.id, "day": day})
        return challenge

    async def get_today_challenge(self, moment: datetime | None = None) -> Challenge | None:
        current_time = moment or now_in_timezone(self.timezone_name)
        start, end = day_window(current_time)
        return await self.challenges.get_active_for_window(start, end)

    async def get_current_challenge(self, moment: datetime | None = None) -> Challenge | None:
        current_time = moment or now_in_timezone(self.timezone_name)
        return await self.challenges.get_latest_active_before(current_time)

    async def get_due_challenges(self, moment: datetime | None = None) -> list[Challenge]:
        current_time = moment or now_in_timezone(self.timezone_name)
        return await self.challenges.get_due_challenges(current_time)

    async def mark_sent(self, challenge: Challenge, sent_at: datetime | None = None) -> Challenge:
        sent_time = sent_at or now_in_timezone(self.timezone_name)
        challenge = await self.challenges.mark_sent(challenge, sent_time)
        await self.session.commit()
        logger.info("Marked challenge as sent", extra={"challenge_id": challenge.id, "day": challenge.day})
        return challenge

    async def list_active_challenges(self) -> list[Challenge]:
        return await self.challenges.list_active()
