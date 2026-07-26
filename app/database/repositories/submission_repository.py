from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from app.database.models.submission import Submission
from app.database.repositories.base import BaseRepository


class SubmissionRepository(BaseRepository[Submission]):
    model = Submission

    async def get_by_user_and_challenge(self, user_id: int, challenge_id: int) -> Submission | None:
        statement = select(Submission).where(
            Submission.user_id == user_id,
            Submission.challenge_id == challenge_id,
        )
        return await self.session.scalar(statement)

    async def create_submission(
        self,
        user_id: int,
        challenge_id: int,
        answer: str,
        submitted_at: datetime,
        is_late: bool,
    ) -> Submission:
        submission = Submission(
            user_id=user_id,
            challenge_id=challenge_id,
            answer=answer,
            submitted_at=submitted_at,
            is_late=is_late,
        )
        return await self.add(submission)

    async def update_submission(
        self,
        submission: Submission,
        answer: str,
        submitted_at: datetime,
        is_late: bool,
    ) -> Submission:
        submission.answer = answer
        submission.submitted_at = submitted_at
        submission.is_late = is_late
        await self.session.flush()
        return submission

    async def count_between(self, start: datetime, end: datetime) -> int:
        value = await self.session.scalar(
            select(func.count(Submission.id)).where(
                Submission.submitted_at >= start,
                Submission.submitted_at < end,
            )
        )
        return int(value or 0)

    async def count_late_for_challenge(self, challenge_id: int) -> int:
        value = await self.session.scalar(
            select(func.count(Submission.id)).where(
                Submission.challenge_id == challenge_id,
                Submission.is_late.is_(True),
            )
        )
        return int(value or 0)

    async def count_on_time_for_challenge(self, challenge_id: int) -> int:
        value = await self.session.scalar(
            select(func.count(Submission.id)).where(
                Submission.challenge_id == challenge_id,
                Submission.is_late.is_(False),
            )
        )
        return int(value or 0)

    async def count_for_challenge(self, challenge_id: int) -> int:
        value = await self.session.scalar(
            select(func.count(Submission.id)).where(Submission.challenge_id == challenge_id)
        )
        return int(value or 0)
