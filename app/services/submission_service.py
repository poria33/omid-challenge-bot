from __future__ import annotations

from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.challenge import Challenge
from app.database.models.submission import Submission
from app.database.models.user import UserStatus
from app.database.repositories.challenge_repository import ChallengeRepository
from app.database.repositories.submission_repository import SubmissionRepository
from app.database.repositories.user_repository import UserRepository
from app.services.exceptions import NoActiveChallengeError, NotRegisteredError, UserBlockedError, ValidationError
from app.services.time import ensure_aware, now_in_timezone

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SubmissionResult:
    submission: Submission
    challenge: Challenge
    is_late: bool
    updated_existing: bool


class SubmissionService:
    def __init__(
        self,
        users: UserRepository,
        challenges: ChallengeRepository,
        submissions: SubmissionRepository,
        session: AsyncSession,
        timezone_name: str,
    ) -> None:
        self.users = users
        self.challenges = challenges
        self.submissions = submissions
        self.session = session
        self.timezone_name = timezone_name

    async def submit_answer_for_current_challenge(self, telegram_id: int, answer: str) -> SubmissionResult:
        normalized_answer = answer.strip()
        if not normalized_answer:
            raise ValidationError("Answer cannot be empty.")

        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            raise NotRegisteredError("User is not registered.")
        if user.status == UserStatus.BLOCKED.value:
            raise UserBlockedError("Blocked users cannot submit answers.")
        if user.status != UserStatus.ACTIVE.value:
            raise NotRegisteredError("User is not active.")

        submitted_at = now_in_timezone(self.timezone_name)
        challenge = await self.challenges.get_latest_active_before(submitted_at)
        if not challenge:
            raise NoActiveChallengeError("There is no active challenge for submissions.")

        deadline = ensure_aware(challenge.deadline, self.timezone_name)
        is_late = submitted_at > deadline

        existing_submission = await self.submissions.get_by_user_and_challenge(user.id, challenge.id)
        if existing_submission:
            submission = await self.submissions.update_submission(
                existing_submission,
                normalized_answer,
                submitted_at,
                is_late,
            )
            updated_existing = True
        else:
            submission = await self.submissions.create_submission(
                user_id=user.id,
                challenge_id=challenge.id,
                answer=normalized_answer,
                submitted_at=submitted_at,
                is_late=is_late,
            )
            updated_existing = False

        await self.session.commit()
        await self.submissions.refresh(submission)
        logger.info(
            "Stored submission",
            extra={
                "submission_id": submission.id,
                "user_id": user.id,
                "challenge_id": challenge.id,
                "is_late": is_late,
                "updated_existing": updated_existing,
            },
        )
        return SubmissionResult(
            submission=submission,
            challenge=challenge,
            is_late=is_late,
            updated_existing=updated_existing,
        )
