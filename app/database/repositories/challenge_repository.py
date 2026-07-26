from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.database.models.challenge import Challenge
from app.database.repositories.base import BaseRepository


class ChallengeRepository(BaseRepository[Challenge]):
    model = Challenge

    async def create_challenge(
        self,
        day: int,
        title: str,
        description: str,
        send_time: datetime,
        deadline: datetime,
        is_active: bool = True,
    ) -> Challenge:
        challenge = Challenge(
            day=day,
            title=title,
            description=description,
            send_time=send_time,
            deadline=deadline,
            is_active=is_active,
        )
        return await self.add(challenge)

    async def get_by_day(self, day: int) -> Challenge | None:
        return await self.session.scalar(select(Challenge).where(Challenge.day == day))

    async def get_active_for_window(self, start: datetime, end: datetime) -> Challenge | None:
        statement = (
            select(Challenge)
            .where(
                Challenge.is_active.is_(True),
                Challenge.send_time >= start,
                Challenge.send_time < end,
            )
            .order_by(Challenge.send_time.desc(), Challenge.day.desc())
            .limit(1)
        )
        return await self.session.scalar(statement)

    async def get_latest_active_before(self, moment: datetime) -> Challenge | None:
        statement = (
            select(Challenge)
            .where(Challenge.is_active.is_(True), Challenge.send_time <= moment)
            .order_by(Challenge.send_time.desc(), Challenge.day.desc())
            .limit(1)
        )
        return await self.session.scalar(statement)

    async def get_due_challenges(self, moment: datetime, limit: int = 20) -> list[Challenge]:
        statement = (
            select(Challenge)
            .where(
                Challenge.is_active.is_(True),
                Challenge.sent_at.is_(None),
                Challenge.send_time <= moment,
                Challenge.deadline >= moment,
            )
            .order_by(Challenge.send_time.asc(), Challenge.day.asc())
            .limit(limit)
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_active(self) -> list[Challenge]:
        result = await self.session.scalars(
            select(Challenge).where(Challenge.is_active.is_(True)).order_by(Challenge.day.asc())
        )
        return list(result.all())

    async def mark_sent(self, challenge: Challenge, sent_at: datetime) -> Challenge:
        challenge.sent_at = sent_at
        await self.session.flush()
        return challenge
