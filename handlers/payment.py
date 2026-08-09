import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

import database as db
import texts
import keyboards as kb
from config import TARIFFS, CARD_NUMBER, ADMIN_ID

router = Router()

QR_PATH = os.path.join(os.path.dirname(os.path.dirname(file)), "qr_payment.png")


@router.message(F.text == "💳 Оплата")
async def payment_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer(texts.NOT_REGISTERED)
        return
    await message.answer(texts.CHOOSE_TARIFF, reply_markup=kb.tariff_kb())


@router.callback_query(F.data.startswith("tariff:"))
async def tariff_chosen(call: CallbackQuery, state: FSMContext):
    key = call.data.split(":")[1]
    tariff = TARIFFS[key]
    await state.update_data(tariff_key=key)

    text = texts.tariff_chosen_text(tariff["label"], tariff["price"]) + (
        f"\n\n💳 Карта: {CARD_NUMBER}"
    )

    if os.path.exists(QR_PATH):
        await call.message.answer_photo(
            FSInputFile(QR_PATH),
            caption=text,
            reply_markup=kb.paid_confirm_kb(),
        )
    else:
        await call.message.answer(text, reply_markup=kb.paid_confirm_kb())

    await call.answer()


@router.callback_query(F.data == "paid_confirm")
async def paid_confirm(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    key = data.get("tariff_key")
    if not key:
        await call.answer("Сначала выбери тариф", show_alert=True)
        return

    tariff = TARIFFS[key]
    user_id = call.from_user.id
    username = f"@{call.from_user.username}" if call.from_user.username else "(нет юзернейма)"

    payment_id = await db.create_payment(user_id, key, tariff["price"], tariff["days"])
    await state.clear()

    await call.message.answer(texts.PAYMENT_SENT_TO_USER)

    user = await db.get_user(user_id)
    mc_nick = user["mc_nick"] if user else "?"

    await bot.send_message(
        ADMIN_ID,
        f"💰 Игрок сообщил об оплате\n\n"
        f"Ник: {mc_nick}\n"
        f"Telegram: {username} (id: {user_id})\n"
        f"Тариф: {tariff['label']}\n"
        f"Сумма: {tariff['price']}₽",
        reply_markup=kb.admin_payment_kb(payment_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("pay_ok:"))
async def payment_confirmed(call: CallbackQuery, bot: Bot):
    payment_id = int(call.data.split(":")[1])
    payment = await db.get_payment(payment_id)
    if payment is None or payment["status"] != "pending":
        await call.answer("Платёж уже обработан или не найден", show_alert=True)
        return

    await db.set_payment_status(payment_id, "confirmed")
    new_until = await db.extend_access(payment["user_id"], payment["days"])

    await call.message.edit_text(call.message.text + "\n\n✅ Оплата подтверждена")
    await bot.send_message(payment["user_id"], texts.PAYMENT_CONFIRMED_USER)
    await call.answer("Не забудь добавить игрока обратно в вайтлист!", show_alert=True)
