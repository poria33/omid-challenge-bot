from __future__ import annotations

from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User, UserStatus
from app.database.repositories.user_repository import UserRepository
from app.services.exceptions import CapacityFullError, UserBlockedError, ValidationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegistrationStatus:
    user: User | None
    registered: bool
    capacity_full: bool
    remaining_capacity: int


class RegistrationService:
    def __init__(self, users: UserRepository, session: AsyncSession, max_users: int) -> None:
        self.users = users
        self.session = session
        self.max_users = max_users

    async def check_registration(self, telegram_id: int) -> RegistrationStatus:
        user = await self.users.get_by_telegram_id(telegram_id)
        active_count = await self.users.count_active()
        remaining_capacity = max(self.max_users - active_count, 0)

        if user and user.status == UserStatus.ACTIVE.value:
            return RegistrationStatus(
                user=user,
                registered=True,
                capacity_full=False,
                remaining_capacity=remaining_capacity,
            )

        return RegistrationStatus(
            user=user,
            registered=False,
            capacity_full=remaining_capacity <= 0,
            remaining_capacity=remaining_capacity,
        )

    async def register_user(self, telegram_id: int, name: str, phone: str) -> User:
        normalized_name = name.strip()
        normalized_phone = phone.strip()

        if len(normalized_name) < 2:
            raise ValidationError("Name must contain at least two characters.")
        if len(normalized_phone) < 5:
            raise ValidationError("Phone number is invalid.")

        existing_user = await self.users.get_by_telegram_id(telegram_id)
        if existing_user and existing_user.status == UserStatus.BLOCKED.value:
            raise UserBlockedError("Blocked users cannot register again.")

        if existing_user and existing_user.status == UserStatus.ACTIVE.value:
            user = await self.users.update_profile(existing_user, normalized_name, normalized_phone)
            await self.session.commit()
            await self.users.refresh(user)
            logger.info("Updated existing user profile", extra={"telegram_id": telegram_id})
            return user

        active_count = await self.users.count_active()
        if active_count >= self.max_users:
            raise CapacityFullError("Challenge capacity is full.")

        user = await self.users.create_user(
            telegram_id=telegram_id,
            name=normalized_name,
            phone=normalized_phone,
        )
        await self.session.commit()
        await self.users.refresh(user)
        logger.info("Registered new user", extra={"telegram_id": telegram_id, "user_id": user.id})
        return user
