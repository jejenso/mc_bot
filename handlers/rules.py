from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb

router = Router()


@router.message(F.text == "📜 Правила")
async def rules_menu(message: Message):
    await message.answer(texts.RULES_MENU, reply_markup=kb.rules_kb())


@router.callback_query(F.data == "rules:server")
async def rules_server(call: CallbackQuery):
    await call.message.answer(texts.RULES_SERVER)
    await call.answer()


@router.callback_query(F.data == "rules:tgk")
async def rules_tgk(call: CallbackQuery):
    await call.message.answer(texts.RULES_TGK)
    await call.answer()
