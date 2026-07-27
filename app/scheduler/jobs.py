from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.database.models.challenge import Challenge
from app.database.models.user import User
from app.database.session import async_session_factory
from app.core.logger import logger
from app.bot.runner import bot


async def send_due_challenges():
    async with async_session_factory() as session:

        now = datetime.now()

        result = await session.execute(
            select(Challenge).where(
                Challenge.is_active == True,
                Challenge.sent_at == None,
                Challenge.send_time <= now,
            )
        )

        challenges = result.scalars().all()

        if not challenges:
            return


        users_result = await session.execute(
            select(User).where(
                User.status == "active"
            )
        )

        users = users_result.scalars().all()


        for challenge in challenges:

            text = (
                f"🔥 چالش روز {challenge.day}\n\n"
                f"{challenge.title}\n\n"
                f"{challenge.description}\n\n"
                "تمرین را انجام دهید و پاسخ خود را ارسال کنید."
            )


            for user in users:

                try:

                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text,
                    )

                except Exception as e:

                    logger.error(
                        f"Send challenge failed "
                        f"user={user.telegram_id}: {e}"
                    )


            challenge.sent_at = now


        await session.commit()