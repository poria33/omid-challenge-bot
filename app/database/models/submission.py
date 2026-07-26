from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.challenge import Challenge
    from app.database.models.user import User


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_submission_user_challenge"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_late: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)

    user: Mapped[User] = relationship("User", back_populates="submissions")
    challenge: Mapped[Challenge] = relationship("Challenge", back_populates="submissions")

    def __repr__(self) -> str:
        return f"Submission(id={self.id!r}, user_id={self.user_id!r}, challenge_id={self.challenge_id!r}, is_late={self.is_late!r})"
