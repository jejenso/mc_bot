from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import database as db
from config import ADMIN_ID, ADMIN_USERNAME
from yoomoney_client import poll_yoomoney


async def check_debts(bot: Bot):
    players = await db.get_all_confirmed_players()
    for p in players:
        stats = await db.get_player_stats(p["tg_id"])
        if not stats:
            continue
        debt_days = stats["debt_days"]

        if debt_days == 0:
            if p["warned_day6"] or p["mentioned_day7"]:
                await db.set_debt_flags(p["tg_id"], warned_day6=0, mentioned_day7=0)
            continue

        if debt_days >= 6 and not p["warned_day6"]:
            await db.set_debt_flags(p["tg_id"], warned_day6=1)
            try:
                await bot.send_message(
                    p["tg_id"],
                    f"⚠️ У тебя долг {debt_days} дн. по оплате сервера. "
                    f"Пожалуйста, пополни баланс, иначе доступ может быть ограничен.",
                )
            except Exception:
                pass

        if debt_days >= 7 and not p["mentioned_day7"] and ADMIN_ID:
            await db.set_debt_flags(p["tg_id"], mentioned_day7=1)
            mention = f"@{ADMIN_USERNAME}" if ADMIN_USERNAME else "администратор"
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"🔴 {mention}, у игрока {p['mc_nick']} долг {debt_days} дн. "
                    f"Требуется решение (бан до погашения долга).",
                )
            except Exception:
                pass


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(check_debts, "cron", hour=12, minute=0, args=[bot])
    scheduler.add_job(poll_yoomoney, "interval", minutes=5, args=[bot])
    return scheduler
