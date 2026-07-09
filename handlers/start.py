from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import MAIN_MENU
from states import Registration

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    player = await db.get_player(message.from_user.id)

    if player is None:
        await message.answer(
            "Привет! 👋 Это бот учёта оплаты Minecraft-сервера.\n\n"
            "Для начала нужно зарегистрироваться.\n"
            "Напиши своё <b>ФИО</b> (так же, как будешь указывать в переводах ЮMoney):"
        )
        await state.set_state(Registration.waiting_full_name)
        return

    if player["status"] == "pending":
        await message.answer("Твоя заявка уже отправлена, ожидай подтверждения администратора ⏳")
        return

    if player["status"] == "rejected":
        await message.answer("Твоя заявка была отклонена. Обратись к администратору.")
        return

    if player["status"] == "banned":
        await message.answer("Ты временно заблокирован. Обратись к администратору.")
        return

    await message.answer(
        f"С возвращением, {player['mc_nick']}! Выбери раздел в меню ниже 👇",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    player = await db.get_player(message.from_user.id)
    if player and player["status"] == "confirmed":
        await message.answer("Главное меню:", reply_markup=MAIN_MENU)
