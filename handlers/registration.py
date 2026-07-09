from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from config import ADMIN_ID
from keyboards import admin_confirm_kb, MAIN_MENU
from states import Registration

router = Router()


@router.message(Registration.waiting_full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if len(full_name.split()) < 2:
        await message.answer("Похоже, это не похоже на ФИО. Введи, пожалуйста, Фамилию и Имя полностью:")
        return

    await state.update_data(full_name=full_name)
    await message.answer("Отлично! Теперь введи свой <b>ник в Minecraft</b>:")
    await state.set_state(Registration.waiting_mc_nick)


@router.message(Registration.waiting_mc_nick)
async def process_mc_nick(message: Message, state: FSMContext, bot: Bot):
    mc_nick = message.text.strip()
    data = await state.get_data()
    full_name = data["full_name"]
    await state.clear()

    existing = await db.get_player(message.from_user.id)
    if existing:
        await message.answer("Ты уже подавал заявку ранее.")
        return

    await db.add_pending_player(
        tg_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=full_name,
        mc_nick=mc_nick,
    )

    await message.answer("Заявка отправлена, ожидайте подтверждения администратора ⏳")

    if ADMIN_ID:
        username_part = f"@{message.from_user.username}" if message.from_user.username else f"id{message.from_user.id}"
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Новая заявка на регистрацию:\n"
            f"Telegram: {username_part}\n"
            f"ФИО: {full_name}\n"
            f"Ник в Minecraft: {mc_nick}",
            reply_markup=admin_confirm_kb(message.from_user.id),
        )


@router.callback_query(F.data.startswith("adm_confirm:"))
async def adm_confirm(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Только администратор может это делать.", show_alert=True)
        return

    tg_id = int(callback.data.split(":")[1])
    await db.confirm_player(tg_id)
    await callback.message.edit_text(callback.message.text + "\n\n✅ Подтверждено")
    await callback.answer("Игрок подтверждён")

    await bot.send_message(
        tg_id,
        "Вы успешно зарегистрированы! Теперь вы можете пользоваться ботом 🎉",
        reply_markup=MAIN_MENU,
    )


@router.callback_query(F.data.startswith("adm_reject:"))
async def adm_reject(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Только администратор может это делать.", show_alert=True)
        return

    tg_id = int(callback.data.split(":")[1])
    await db.reject_player(tg_id)
    await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонено")
    await callback.answer("Заявка отклонена")

    await bot.send_message(tg_id, "Ваша заявка отклонена, обратитесь к администратору.")
