from __future__ import annotations

from dataclasses import dataclass

from app.database.repositories.challenge_repository import ChallengeRepository
from app.database.repositories.submission_repository import SubmissionRepository
from app.database.repositories.user_repository import UserRepository
from app.services.time import day_window, ensure_aware, now_in_timezone


@dataclass(frozen=True)
class DashboardMetrics:
    total_users: int
    remaining_capacity: int
    active_challenge_day: int | None
    today_submissions: int
    late_users_count: int


class MetricsService:
    def __init__(
        self,
        users: UserRepository,
        challenges: ChallengeRepository,
        submissions: SubmissionRepository,
        max_users: int,
        timezone_name: str,
    ) -> None:
        self.users = users
        self.challenges = challenges
        self.submissions = submissions
        self.max_users = max_users
        self.timezone_name = timezone_name

    async def get_dashboard_metrics(self) -> DashboardMetrics:
        current_time = now_in_timezone(self.timezone_name)
        start, end = day_window(current_time)

        total_users = await self.users.count_active()
        today_submissions = await self.submissions.count_between(start, end)
        challenge = await self.challenges.get_active_for_window(start, end)
        if not challenge:
            challenge = await self.challenges.get_latest_active_before(current_time)

        late_users_count = 0
        active_challenge_day: int | None = None
        if challenge:
            active_challenge_day = challenge.day
            deadline = ensure_aware(challenge.deadline, self.timezone_name)
            if current_time > deadline:
                on_time_count = await self.submissions.count_on_time_for_challenge(challenge.id)
                late_users_count = max(total_users - on_time_count, 0)
            else:
                late_users_count = await self.submissions.count_late_for_challenge(challenge.id)

        return DashboardMetrics(
            total_users=total_users,
            remaining_capacity=max(self.max_users - total_users, 0),
            active_challenge_day=active_challenge_day,
            today_submissions=today_submissions,
            late_users_count=late_users_count,
        )
