import re
import aiohttp
from aiogram import Bot

import database as db
from config import YOOMONEY_TOKEN, ADMIN_ID

OPERATION_HISTORY_URL = "https://yoomoney.ru/api/operation-history"


def _normalize(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


async def _fetch_operations(records: int = 20):
    headers = {"Authorization": f"Bearer {YOOMONEY_TOKEN}"}
    data = {"records": str(records), "type": "deposition"}
    async with aiohttp.ClientSession() as session:
        async with session.post(OPERATION_HISTORY_URL, headers=headers, data=data) as resp:
            resp.raise_for_status()
            return await resp.json()


def _extract_sender_text(op: dict) -> str:
    """Собирает все текстовые поля операции, где может быть указано имя отправителя."""
    parts = [op.get("title", ""), op.get("comment", ""), op.get("message", ""), op.get("label", "")]
    return _normalize(" ".join(p for p in parts if p))


async def poll_yoomoney(bot: Bot):
    if not YOOMONEY_TOKEN:
        return

    try:
        data = await _fetch_operations()
    except Exception as e:
        if ADMIN_ID:
            await bot.send_message(ADMIN_ID, f"⚠️ Ошибка при опросе ЮMoney: {e}")
        return

    operations = data.get("operations", [])
    if not operations:
        return

    players = await db.get_all_confirmed_players()

    for op in operations:
        op_id = op.get("operation_id")
        if not op_id or await db.is_operation_processed(op_id):
            continue

        # деньги должны прийти нам (положительная сумма - amount без учёта поля direction для deposition)
        amount = op.get("amount", 0)
        sender_text = _extract_sender_text(op)

        matched_player = None
        for p in players:
            if _normalize(p["full_name"]) in sender_text:
                matched_player = p
                break

        if matched_player:
            await db.add_payment(matched_player["id"], float(amount), "yoomoney")
            await db.mark_operation_processed(op_id)
            try:
                await bot.send_message(
                    matched_player["tg_id"],
                    f"✅ Платёж на сумму {amount:.2f} ₽ автоматически зачислен через ЮMoney. Спасибо!",
                )
            except Exception:
                pass
        else:
            # не смогли сопоставить — сообщаем администратору, чтобы подтвердил вручную через /confirm
            await db.mark_operation_processed(op_id)
            if ADMIN_ID:
                await bot.send_message(
                    ADMIN_ID,
                    f"💸 Пришёл платёж {amount:.2f} ₽, не удалось автоматически определить игрока.\n"
                    f"Данные операции: {sender_text or 'нет данных'}\n"
                    f"Если это оплата за сервер — подтверди вручную: /confirm @username сумма",
                )
