from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

import database as db
from config import ADMIN_ID

router = Router()


def _is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


async def _resolve_tg_id(bot: Bot, username: str):
    """Пытается найти tg_id игрока по username, сохранённому в базе при регистрации."""
    username = username.lstrip("@")
    import aiosqlite
    async with aiosqlite.connect(db.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT tg_id FROM players WHERE username = ?", (username,))
        row = await cur.fetchone()
        return row["tg_id"] if row else None


@router.message(Command("setplayers"))
async def cmd_setplayers(message: Message):
    if not _is_admin(message):
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /setplayers 6")
        return
    await db.set_setting("player_count_override", parts[1])
    rate = await db.get_daily_rate()
    await message.answer(f"Количество игроков обновлено: {parts[1]}. Стоимость дня: {rate:.2f} ₽")


@router.message(Command("confirm"))
async def cmd_confirm_payment(message: Message, bot: Bot):
    if not _is_admin(message):
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /confirm @username сумма")
        return
    username, amount_str = parts[1], parts[2]
    try:
        amount = float(amount_str.replace(",", "."))
    except ValueError:
        await message.answer("Сумма указана неверно.")
        return

    tg_id = await _resolve_tg_id(bot, username)
    if not tg_id:
        await message.answer("Игрок с таким username не найден в базе.")
        return

    player = await db.get_player(tg_id)
    await db.add_payment(player["id"], amount, "manual")
    await message.answer(f"Платёж {amount:.2f} ₽ засчитан игроку {player['mc_nick']}.")
    await bot.send_message(tg_id, f"Администратор подтвердил ваш платёж: {amount:.2f} ₽ ✅")


@router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if not _is_admin(message):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("Использование: /ban @username причина")
        return
    username = parts[1]
    reason = parts[2] if len(parts) > 2 else "не указана"
    tg_id = await _resolve_tg_id(bot, username)
    if not tg_id:
        await message.answer("Игрок не найден.")
        return
    await db.ban_player(tg_id)
    await message.answer(f"Игрок {username} забанен. Причина: {reason}")
    await bot.send_message(tg_id, f"Вы были временно заблокированы. Причина: {reason}")


@router.message(Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
    if not _is_admin(message):
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /unban @username")
        return
    tg_id = await _resolve_tg_id(bot, parts[1])
    if not tg_id:
        await message.answer("Игрок не найден.")
        return
    await db.unban_player(tg_id)
    await message.answer(f"Игрок {parts[1]} разблокирован.")
    await bot.send_message(tg_id, "Вы снова можете пользоваться сервером ✅")


@router.message(Command("addplayer"))
async def cmd_addplayer(message: Message):
    if not _is_admin(message):
        return
    # /addplayer @username ник_в_майнкрафте Имя Фамилия
    parts = message.text.split(maxsplit=3)
    if len(parts) != 4:
        await message.answer("Использование: /addplayer @username ник_в_майнкрафте Имя Фамилия")
        return
    username = parts[1].lstrip("@")
    mc_nick = parts[2]
    full_name = parts[3]

    # Если это команда для себя (администратора) и tg_id неизвестен — используем ID администратора,
    # либо ставим временный отрицательный id, который нужно будет поправить после первого /start игрока.
    existing = None
    import aiosqlite
    async with aiosqlite.connect(db.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT tg_id FROM players WHERE username = ?", (username,))
        existing = await cur.fetchone()

    if existing:
        await message.answer("Такой игрок уже есть в базе.")
        return

    if username.lower() == (message.from_user.username or "").lower():
        tg_id = message.from_user.id
    else:
        await message.answer(
            "⚠️ Игрок ещё не писал боту, поэтому его Telegram ID неизвестен.\n"
            "Попроси его отправить боту /start — заявка придёт тебе автоматически, "
            "и её можно будет подтвердить кнопкой."
        )
        return

    await db.add_confirmed_player(tg_id, username, full_name, mc_nick)
    await message.answer(f"Игрок {mc_nick} ({full_name}) добавлен и подтверждён.")


@router.message(Command("removeplayer"))
async def cmd_removeplayer(message: Message, bot: Bot):
    if not _is_admin(message):
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /removeplayer @username")
        return
    tg_id = await _resolve_tg_id(bot, parts[1])
    if not tg_id:
        await message.answer("Игрок не найден.")
        return
    await db.remove_player(tg_id)
    await message.answer(f"Игрок {parts[1]} удалён из базы.")
