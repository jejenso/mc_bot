from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
import texts
from keyboards import profile_kb, back_kb, instructions_kb, MAIN_MENU

router = Router()


async def _require_confirmed(message: Message):
    player = await db.get_player(message.from_user.id)
    if not player or player["status"] != "confirmed":
        await message.answer("Сначала нужно зарегистрироваться: отправь /start")
        return None
    return player


def _profile_text(stats: dict) -> str:
    player = stats["player"]
    text = (
        f"<b>👤 Профиль</b>\n\n"
        f"Ник в Minecraft: <b>{player['mc_nick']}</b>\n"
        f"Всего внесено: <b>{stats['total_paid']:.2f} ₽</b>\n"
        f"Остаток (не идёт в полные дни): <b>{stats['remainder']:.2f} ₽</b>\n"
        f"Оплачено дней: <b>{stats['paid_days']}</b>\n"
    )
    if stats["debt_days"] > 0:
        text += f"⚠️ Долг: <b>{stats['debt_days']} дн.</b>\n"
    else:
        text += "Долгов нет ✅\n"
    return text


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    player = await _require_confirmed(message)
    if not player:
        return
    stats = await db.get_player_stats(message.from_user.id)
    await message.answer(_profile_text(stats), reply_markup=profile_kb())


@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    stats = await db.get_player_stats(callback.from_user.id)
    if not stats:
        await callback.answer()
        return
    await callback.message.edit_text(_profile_text(stats), reply_markup=profile_kb())
    await callback.answer()


@router.callback_query(F.data == "topup")
async def show_topup(callback: CallbackQuery):
    await callback.message.edit_text(texts.instr_topup_text(), reply_markup=back_kb())
    await callback.answer()


@router.message(F.text == "💰 Баланс сервера")
async def show_server_balance(message: Message):
    player = await _require_confirmed(message)
    if not player:
        return

    total = await db.get_total_server_paid()
    daily_rate = await db.get_daily_rate()
    count = await db.get_active_player_count()
    total_days = int(total // (daily_rate * count)) if daily_rate * count > 0 else 0

    players = await db.get_all_confirmed_players()
    lines = []
    for p in players:
        paid = await db.get_total_paid(p["id"])
        lines.append(f"• {p['mc_nick']}: {paid:.2f} ₽")

    text = (
        f"<b>💰 Баланс сервера</b>\n\n"
        f"Активных игроков: <b>{count}</b>\n"
        f"Стоимость дня на игрока: <b>{daily_rate:.2f} ₽</b>\n"
        f"Всего внесено всеми: <b>{total:.2f} ₽</b>\n"
        f"Оплачено дней вперёд: <b>{total_days}</b>\n\n"
        f"<b>Вклад игроков:</b>\n" + "\n".join(lines)
    )
    await message.answer(text)


@router.message(F.text == "📜 Правила")
async def show_rules(message: Message):
    player = await _require_confirmed(message)
    if not player:
        return
    await message.answer(texts.RULES_TEXT)


@router.message(F.text == "📖 Инструкции")
async def show_instructions(message: Message):
    player = await _require_confirmed(message)
    if not player:
        return
    await message.answer("Выбери, что тебя интересует:", reply_markup=instructions_kb())


@router.callback_query(F.data == "instr_join")
async def instr_join(callback: CallbackQuery):
    await callback.message.edit_text(texts.instr_join_text(), reply_markup=instructions_kb())
    await callback.answer()


@router.callback_query(F.data == "instr_mods")
async def instr_mods(callback: CallbackQuery):
    await callback.message.edit_text(texts.instr_mods_text(), reply_markup=instructions_kb())
    await callback.answer()


@router.callback_query(F.data == "instr_topup")
async def instr_topup(callback: CallbackQuery):
    await callback.message.edit_text(texts.instr_topup_text(), reply_markup=instructions_kb())
    await callback.answer()


@router.callback_query(F.data == "instr_register")
async def instr_register(callback: CallbackQuery):
    await callback.message.edit_text(texts.instr_register_text(), reply_markup=instructions_kb())
    await callback.answer()
