from aiogram import Router, F
from aiogram.types import Message

import database as db
import texts
import timeutils

router = Router()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer(texts.NOT_REGISTERED)
        return

    days, hours, expired = timeutils.time_left(user["access_until"])
    offset = timeutils.effective_offset(user)
    await message.answer(
        texts.profile_text(user["full_name"], user["mc_nick"], user["created_at"], days, hours, expired, offset)
    )
