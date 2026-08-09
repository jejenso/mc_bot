import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command

import database as db
import texts
from config import ADMIN_ID

router = Router()
router.message.filter(F.from_user.id == ADMIN_ID)


@router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer(texts.ADMIN_USAGE_BAN)
        return

    nick = parts[1]
    reason = parts[2] if len(parts) > 2 else ""

    user = await db.get_user_by_nick(nick)
    if user is None:
        await message.answer(texts.ADMIN_USER_NOT_FOUND)
        return

    await db.set_user_status(user["user_id"], "banned", None)
    await message.answer(texts.admin_ban_done(user["mc_nick"], reason))

    try:
        await bot.send_message(user["user_id"], texts.user_banned_notice(reason))
    except Exception:
        pass


@router.message(Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(texts.ADMIN_USAGE_UNBAN)
        return

    nick = parts[1]
    user = await db.get_user_by_nick(nick)
    if user is None:
        await message.answer(texts.ADMIN_USER_NOT_FOUND)
        return

    await db.set_user_status(user["user_id"], "approved", None)
    await message.answer(texts.admin_unban_done(user["mc_nick"]))

    try:
        await bot.send_message(user["user_id"], texts.USER_UNBANNED_NOTICE)
    except Exception:
        pass


@router.message(Command("extend"))
async def cmd_extend(message: Message, bot: Bot):
    parts = message.text.split()
    if len(parts) != 3 or not parts[2].isdigit():
        await message.answer(texts.ADMIN_USAGE_EXTEND)
        return

    nick, days = parts[1], int(parts[2])
    user = await db.get_user_by_nick(nick)
    if user is None:
        await message.answer(texts.ADMIN_USER_NOT_FOUND)
        return

    new_until = await db.extend_access(user["user_id"], days)
    await message.answer(texts.admin_extend_done(user["mc_nick"], days, new_until.strftime("%d.%m.%Y %H:%M")))

    try:
        await bot.send_message(user["user_id"], texts.user_days_changed_notice(days, added=True))
    except Exception:
        pass


@router.message(Command("reduce"))
async def cmd_reduce(message: Message, bot: Bot):
    parts = message.text.split()
    if len(parts) != 3 or not parts[2].isdigit():
        await message.answer(texts.ADMIN_USAGE_REDUCE)
        return

    nick, days = parts[1], int(parts[2])
    user = await db.get_user_by_nick(nick)
    if user is None:
        await message.answer(texts.ADMIN_USER_NOT_FOUND)
        return

    new_until = await db.reduce_access(user["user_id"], days)
    await message.answer(texts.admin_reduce_done(user["mc_nick"], days, new_until.strftime("%d.%m.%Y %H:%M")))

    try:
        await bot.send_message(user["user_id"], texts.user_days_changed_notice(days, added=False))
    except Exception:
        pass


@router.message(Command("info"))
async def cmd_info(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(texts.ADMIN_USAGE_INFO)
        return

    nick = parts[1]
    user = await db.get_user_by_nick(nick)
    if user is None:
        await message.answer(texts.ADMIN_USER_NOT_FOUND)
        return

    await message.answer(texts.admin_info_text(user))


@router.message(Command("players"))
async def cmd_players(message: Message):
    users = await db.get_all_users()
    await message.answer(texts.admin_players_list(users))
