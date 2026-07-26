from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.bot.keyboards.contact import contact_keyboard
from app.bot.states.registration import RegistrationStates
from app.database.models.user import UserStatus
from app.services.exceptions import CapacityFullError, UserBlockedError, ValidationError
from app.services.registration_service import RegistrationService

router = Router(name="registration")

CAPACITY_FULL_MESSAGE = "❌ ظرفیت چالش تکمیل شده است."


@router.message(CommandStart())
async def start_command(
    message: Message,
    state: FSMContext,
    registration_service: RegistrationService,
) -> None:
    await state.clear()
    if not message.from_user:
        return

    status = await registration_service.check_registration(message.from_user.id)
    if status.user and status.user.status == UserStatus.BLOCKED.value:
        await message.answer("⛔️ دسترسی شما به چالش مسدود شده است.", reply_markup=ReplyKeyboardRemove())
        return

    if status.registered:
        await message.answer(
            "✅ شما قبلاً در چالش امید ثبت‌نام کرده‌اید.\n"
            "هر روز تمرین برای شما ارسال می‌شود. پاسخ خود را همین‌جا ارسال کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if status.capacity_full:
        await message.answer(CAPACITY_FULL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return

    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer(
        "به چالش امید خوش آمدید 🌟\n\n"
        "برای شروع ثبت‌نام، لطفاً نام و نام خانوادگی خود را ارسال کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(RegistrationStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("لطفاً نام معتبر وارد کنید.")
        return

    await state.update_data(name=name)
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        "ممنون. حالا برای تکمیل ثبت‌نام، شماره تماس خود را با دکمه زیر ارسال کنید.",
        reply_markup=contact_keyboard(),
    )


@router.message(RegistrationStates.waiting_for_name)
async def process_invalid_name(message: Message) -> None:
    await message.answer("لطفاً نام خود را به صورت متن ارسال کنید.")


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone(
    message: Message,
    state: FSMContext,
    registration_service: RegistrationService,
) -> None:
    if not message.from_user or not message.contact:
        return

    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await message.answer("لطفاً شماره تماس متعلق به حساب تلگرام خودتان را ارسال کنید.")
        return

    data = await state.get_data()
    name = str(data.get("name", "")).strip()
    phone = message.contact.phone_number.strip()

    try:
        await registration_service.register_user(
            telegram_id=message.from_user.id,
            name=name,
            phone=phone,
        )
    except CapacityFullError:
        await state.clear()
        await message.answer(CAPACITY_FULL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return
    except UserBlockedError:
        await state.clear()
        await message.answer("⛔️ دسترسی شما به چالش مسدود شده است.", reply_markup=ReplyKeyboardRemove())
        return
    except ValidationError:
        await message.answer("اطلاعات ارسال‌شده معتبر نیست. لطفاً دوباره تلاش کنید.")
        return

    await state.clear()
    await message.answer(
        "✅ ثبت‌نام شما با موفقیت انجام شد.\n"
        "از این پس تمرین‌های روزانه چالش امید برای شما ارسال می‌شود.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(RegistrationStates.waiting_for_phone)
async def process_invalid_phone(message: Message) -> None:
    await message.answer(
        "برای تکمیل ثبت‌نام باید شماره تماس خود را با دکمه تلگرام ارسال کنید.",
        reply_markup=contact_keyboard(),
    )
