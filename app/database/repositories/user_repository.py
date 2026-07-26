from __future__ import annotations

from sqlalchemy import func, select

from app.database.models.user import User, UserStatus
from app.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        statement = select(User).where(User.telegram_id == telegram_id)
        return await self.session.scalar(statement)

    async def create_user(self, telegram_id: int, name: str, phone: str) -> User:
        user = User(
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            status=UserStatus.ACTIVE.value,
        )
        return await self.add(user)

    async def update_profile(self, user: User, name: str, phone: str) -> User:
        user.name = name
        user.phone = phone
        await self.session.flush()
        return user

    async def count_all(self) -> int:
        value = await self.session.scalar(select(func.count(User.id)))
        return int(value or 0)

    async def count_active(self) -> int:
        value = await self.session.scalar(
            select(func.count(User.id)).where(User.status == UserStatus.ACTIVE.value)
        )
        return int(value or 0)

    async def list_active(self, limit: int | None = None, offset: int = 0) -> list[User]:
        statement = (
            select(User)
            .where(User.status == UserStatus.ACTIVE.value)
            .order_by(User.created_at.asc(), User.id.asc())
            .offset(offset)
        )
        if limit is not None:
            statement = statement.limit(limit)
        result = await self.session.scalars(statement)
        return list(result.all())
