from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import texts
import keyboards as kb
from states import ReportForm, AdminVerdict
from config import ADMIN_ID

router = Router()


@router.message(F.text == "🚨 Репорт")
async def report_menu(message: Message):
    await message.answer(texts.REPORT_MENU, reply_markup=kb.report_kb())


@router.callback_query(F.data == "report:server")
async def report_server_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer(texts.REPORT_FORM_SERVER)
    await state.set_state(ReportForm.waiting_text_server)
    await call.answer()


@router.callback_query(F.data == "report:tgk")
async def report_tgk_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer(texts.REPORT_FORM_TGK)
    await state.set_state(ReportForm.waiting_text_tgk)
    await call.answer()


async def _submit_report(message: Message, state: FSMContext, bot: Bot, kind: str, kind_label: str):
    content = message.text
    reporter_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "(нет юзернейма)"

    report_id = await db.create_report(reporter_id, kind, content)
    await state.clear()

    await message.answer(texts.REPORT_SENT_USER)

    await bot.send_message(
        ADMIN_ID,
        f"🚨 Новая жалоба ({kind_label})\n"
        f"От: {username} (id: {reporter_id})\n\n"
        f"{content}",
        reply_markup=kb.admin_report_kb(report_id),
    )


@router.message(ReportForm.waiting_text_server)
async def report_server_submit(message: Message, state: FSMContext, bot: Bot):
    await _submit_report(message, state, bot, "server", "нарушение на сервере")


@router.message(ReportForm.waiting_text_tgk)
async def report_tgk_submit(message: Message, state: FSMContext, bot: Bot):
    await _submit_report(message, state, bot, "tgk", "нарушение в тгк")


@router.callback_query(F.data.startswith("report_review:"))
async def report_review(call: CallbackQuery, state: FSMContext, bot: Bot):
    if call.from_user.id != ADMIN_ID:
        await call.answer()
        return

    report_id = int(call.data.split(":")[1])
    report = await db.get_report(report_id)
    if report is None:
        await call.answer("Жалоба не найдена", show_alert=True)
        return

    await state.update_data(report_id=report_id)
    await state.set_state(AdminVerdict.waiting_verdict)
    await call.message.answer(texts.ADMIN_ASK_VERDICT)

    await bot.send_message(report["reporter_id"], texts.REPORT_UNDER_REVIEW_USER)
    await call.answer()


@router.message(AdminVerdict.waiting_verdict, F.from_user.id == ADMIN_ID)
async def admin_send_verdict(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    report_id = data.get("report_id")
    if not report_id:
        return

    report = await db.get_report(report_id)
    await db.set_report_verdict(report_id, message.text)
    await state.clear()

    await bot.send_message(report["reporter_id"], texts.report_verdict_user(message.text))
    await message.answer(texts.ADMIN_VERDICT_SENT)
