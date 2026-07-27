from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.database.session import async_session_factory
from app.database.models.user import User
from app.database.models.challenge import Challenge
from app.database.models.submission import Submission
from sqlalchemy import select
from datetime import datetime


router = Router(name="submissions")


@router.message(F.text)
async def submit_answer(
    message: Message,
):

    if not message.from_user:
        return

    text = message.text.strip()

    if not text:
        return


    async with async_session_factory() as session:

        user_result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        user = user_result.scalar_one_or_none()


        if not user:
            return


        challenge_result = await session.execute(
            select(Challenge)
            .where(
                Challenge.is_active == True
            )
            .order_by(
                Challenge.day.desc()
            )
        )

        challenge = challenge_result.scalars().first()


        if not challenge:
            await message.answer(
                "در حال حاضر چالشی فعال نیست."
            )
            return


        submission = Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            answer=text,
            submitted_at=datetime.now(),
            is_late=False,
        )


        session.add(submission)

        await session.commit()


    await message.answer(
        "✅ پاسخ شما ثبت شد.\n"
        "ادامه بده، عالی پیش می‌روی 💪"
    )