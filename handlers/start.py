from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import texts
import keyboards as kb
from states import Registration
from config import ADMIN_ID

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)

    if user is None:
        await message.answer(texts.WELCOME_NEW)
        await state.set_state(Registration.waiting_full_name)
        return

    if user["status"] == "pending":
        await message.answer(texts.ALREADY_PENDING)
    elif user["status"] == "banned":
        await message.answer(texts.ALREADY_BANNED)
    elif user["status"] == "rejected":
        # разрешаем подать заявку заново
        await message.answer(texts.WELCOME_NEW)
        await state.set_state(Registration.waiting_full_name)
    else:
        await message.answer(texts.MAIN_MENU_GREETING, reply_markup=kb.main_menu)


@router.message(Registration.waiting_full_name)
async def reg_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await message.answer(texts.ASK_NICK)
    await state.set_state(Registration.waiting_mc_nick)


@router.message(Registration.waiting_mc_nick)
async def reg_mc_nick(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    full_name = data["full_name"]
    mc_nick = message.text.strip()
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "(нет юзернейма)"

    await db.create_pending_user(user_id, full_name, mc_nick)
    await state.clear()

    await message.answer(texts.REG_SENT_TO_USER)

    await bot.send_message(
        ADMIN_ID,
        f"📥 Новая заявка на регистрацию\n\n"
        f"ФИ: {full_name}\n"
        f"Ник в Minecraft: {mc_nick}\n"
        f"Telegram: {username} (id: {user_id})",
        reply_markup=kb.admin_registration_kb(user_id),
    )


@router.callback_query(F.data.startswith("reg_ok:"))
async def reg_approve(call: CallbackQuery, bot: Bot):
    user_id = int(call.data.split(":")[1])
    from config import TRIAL_DAYS
    import datetime
    access_until = datetime.datetime.now() + datetime.timedelta(days=TRIAL_DAYS)
    await db.set_user_status(user_id, "approved", access_until.isoformat())

    await call.message.edit_text(call.message.text + "\n\n✅ Заявка одобрена")
    await bot.send_message(user_id, texts.REG_APPROVED_USER, reply_markup=kb.main_menu)
    await call.answer("Игрок одобрен. Не забудь добавить его ник в вайтлист сервера!", show_alert=True)


@router.callback_query(F.data.startswith("reg_no:"))
async def reg_reject(call: CallbackQuery, bot: Bot):
    user_id = int(call.data.split(":")[1])
    await db.set_user_status(user_id, "rejected")

    await call.message.edit_text(call.message.text + "\n\n❌ Заявка отклонена")
    await bot.send_message(user_id, texts.REG_REJECTED_USER)
    await call.answer("Заявка отклонена")
