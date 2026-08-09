import datetime
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database as db
import texts
from config import ADMIN_ID


async def check_access(bot: Bot):
    """Запускается регулярно: шлёт напоминания и уведомления об истечении срока."""
    users = await db.get_active_users()
    now = datetime.datetime.now()

    for user in users:
        if not user["access_until"]:
            continue
        until = datetime.datetime.fromisoformat(user["access_until"])
        remaining = until - now

        # За 1 день до истечения — напомнить, если ещё не напоминали
        if datetime.timedelta(0) < remaining <= datetime.timedelta(days=1) and not user["notified_soon"]:
            await bot.send_message(user["user_id"], texts.EXPIRY_SOON_USER)
            await db.mark_notified(user["user_id"], "notified_soon")

        # Срок истёк — уведомить игрока и админа один раз
        if remaining <= datetime.timedelta(0) and not user["notified_expired"]:
            await bot.send_message(user["user_id"], texts.EXPIRED_USER)
            await bot.send_message(
                ADMIN_ID,
                f"⛔ У игрока {user['mc_nick']} (id: {user['user_id']}) истёк срок доступа.\n"
                f"Убери его из белого списка сервера.",
            )
            await db.mark_notified(user["user_id"], "notified_expired")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    # Проверка каждые 3 часа — этого достаточно для дневной точности напоминаний
    scheduler.add_job(check_access, "interval", hours=3, args=[bot])
    scheduler.start()
    return scheduler
