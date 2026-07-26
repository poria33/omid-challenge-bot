from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.services.challenge_service import ChallengeService
from app.services.exceptions import NoActiveChallengeError, NotRegisteredError, UserBlockedError, ValidationError
from app.services.registration_service import RegistrationService
from app.services.submission_service import SubmissionService

router = Router(name="submissions")


@router.message(Command("status"))
async def status_command(
    message: Message,
    registration_service: RegistrationService,
    challenge_service: ChallengeService,
) -> None:
    if not message.from_user:
        return

    registration = await registration_service.check_registration(message.from_user.id)
    challenge = await challenge_service.get_current_challenge()

    if not registration.registered:
        await message.answer("شما هنوز ثبت‌نام نکرده‌اید. برای شروع /start را ارسال کنید.")
        return

    if challenge:
        await message.answer(
            "✅ وضعیت شما: ثبت‌نام‌شده\n"
            f"📌 روز فعال چالش: {challenge.day}\n"
            f"📝 عنوان تمرین: {challenge.title}"
        )
        return

    await message.answer("✅ وضعیت شما: ثبت‌نام‌شده\nهنوز تمرین فعالی برای ارسال پاسخ وجود ندارد.")


@router.message(StateFilter(None), F.text)
async def collect_text_submission(
    message: Message,
    submission_service: SubmissionService,
) -> None:
    if not message.from_user or not message.text:
        return

    if message.text.startswith("/"):
        await message.answer("دستور شناخته نشد. برای شروع /start و برای وضعیت /status را ارسال کنید.")
        return

    try:
        result = await submission_service.submit_answer_for_current_challenge(
            telegram_id=message.from_user.id,
            answer=message.text,
        )
    except NotRegisteredError:
        await message.answer("برای ارسال پاسخ ابتدا باید ثبت‌نام کنید. لطفاً /start را ارسال کنید.")
        return
    except UserBlockedError:
        await message.answer("⛔️ دسترسی شما به ارسال پاسخ مسدود شده است.")
        return
    except NoActiveChallengeError:
        await message.answer("در حال حاضر تمرین فعالی برای ثبت پاسخ وجود ندارد.")
        return
    except ValidationError:
        await message.answer("پاسخ شما خالی یا نامعتبر است. لطفاً پاسخ معتبر ارسال کنید.")
        return

    update_text = "به‌روزرسانی شد" if result.updated_existing else "ثبت شد"
    if result.is_late:
        await message.answer(
            f"⚠️ پاسخ شما برای روز {result.challenge.day} با تأخیر {update_text}.\n"
            "پاسخ ذخیره شد اما به عنوان دیرکرد ثبت گردید."
        )
        return

    await message.answer(f"✅ پاسخ شما برای روز {result.challenge.day} با موفقیت {update_text}.")
