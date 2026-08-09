import datetime
from aiogram import Router, F
from aiogram.types import Message

import database as db
import texts

router = Router()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer(texts.NOT_REGISTERED)
        return

    days_left = 0
    if user["access_until"]:
        delta = datetime.datetime.fromisoformat(user["access_until"]) - datetime.datetime.now()
        days_left = max(0, delta.days + (1 if delta.seconds > 0 else 0))

    await message.answer(texts.profile_text(user["full_name"], user["mc_nick"], days_left))
