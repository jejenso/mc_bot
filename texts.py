from config import SERVER_NAME, TRIAL_DAYS
import timeutils

STATUS_RU = {
    "pending": "⏳ Ожидает одобрения",
    "approved": "✅ Одобрен",
    "rejected": "❌ Отклонён",
    "banned": "⛔ Забанен",
}


def status_ru(status: str) -> str:
    return STATUS_RU.get(status, status)


def days_hours_line(days: int, hours: int, expired: bool) -> str:
    """Единый формат для 'сколько осталось' — используется и в профиле, и у админа."""
    if expired:
        return "истёк"
    if days > 0 and hours > 0:
        return f"{days} дн. {hours} ч."
    if days > 0:
        return f"{days} дн."
    return f"{hours} ч."


WELCOME_NEW = (
    f"👋 Привет! Это бот сервера {SERVER_NAME}.\n\n"
    "Чтобы начать играть, нужно зарегистрироваться.\n"
    "Напиши своё Фамилию и Имя (чтобы мы понимали, от кого приходит оплата):"
)

ASK_NICK = "Отлично 👍 Теперь напиши свой ник в Minecraft (точно как в игре):"

ASK_LOCATION = (
    "Последний шаг 📍 Поделись геолокацией — так бот будет показывать тебе "
    "время в твоём часовом поясе (например, когда истекает доступ).\n\n"
    "Это разовая штука, не слежка — можно нажать «Пропустить», тогда время "
    "будет показываться по московскому."
)

LOCATION_SAVED = "✅ Часовой пояс определён, буду показывать время по нему."

LOCATION_FAILED = "Не получилось определить часовой пояс по этим координатам — покажу время по МСК."

LOCATION_SKIPPED = "Хорошо, буду показывать время по московскому (UTC+3)."

REG_SENT_TO_USER = (
    "✅ Заявка отправлена администратору!\n"
    "Дождись, пока её примут — обычно это быстро 🙌"
)

REG_APPROVED_USER = (
    f"🎉 Заявку одобрили! Добро пожаловать на {SERVER_NAME}!\n\n"
    f"Тебе начислено {TRIAL_DAYS} пробных дня — можешь заходить и играть.\n"
    "Скоро тебя добавят в белый список сервера."
)

REG_REJECTED_USER = (
    "😔 Заявку отклонили.\n"
    "Если это ошибка — напиши администратору в личку."
)

ALREADY_PENDING = "⏳ Твоя заявка ещё на рассмотрении, немного подожди."

ALREADY_BANNED = (
    "⛔ Ты забанен на сервере.\n"
    "По вопросам разбана — пиши администратору в личку."
)

MAIN_MENU_GREETING = f"Главное меню {SERVER_NAME} 🎮\nВыбирай, что нужно:"


def profile_text(full_name: str, mc_nick: str, created_at: str, days: int, hours: int, expired: bool, offset_hours: float) -> str:
    if expired:
        days_line = "⏳ Доступ истёк — не забудь оплатить 👇"
    else:
        days_line = f"⏳ Осталось: {days_hours_line(days, hours, expired)}"
    reg_line = f"📅 Зарегистрирован: {timeutils.fmt_iso(created_at, offset_hours)}\n" if created_at else ""
    return (
        "👤 Твой профиль\n\n"
        f"ФИ: {full_name}\n"
        f"Ник в Minecraft: {mc_nick}\n"
        f"{reg_line}"
        f"{days_line}"
    )


TRIAL_EXPIRED_USER = (
    "⌛ Пробные дни закончились!\n"
    "Оплати доступ по любому тарифу, чтобы продолжить играть 🙌"
)

EXPIRY_SOON_USER = (
    "⏰ Напоминание: доступ на сервер заканчивается через 1 день.\n"
    "Продли подписку, чтобы не потерять доступ к серверу 👇"
)

EXPIRY_SOON_HOUR_USER = (
    "⏰ Осталось меньше часа доступа!\n"
    "Успей продлить подписку, чтобы не потерять доступ к серверу 👇"
)

EXPIRED_USER = (
    "⌛ Срок доступа истёк.\n"
    "Оплати, чтобы снова попасть в белый список сервера 👇"
)


def admin_expiry_soon_notice(mc_nick: str, when: str) -> str:
    return f"⏰ У игрока {mc_nick} скоро истечёт доступ ({when})."


def admin_expired_notice(mc_nick: str, user_id: int) -> str:
    return (
        f"⛔ У игрока {mc_nick} (id: {user_id}) истёк срок доступа.\n"
        f"Убери его из белого списка сервера."
    )


CHOOSE_TARIFF = "💳 Для начала выбери тариф:"


def tariff_chosen_text(label: str, price: int) -> str:
    return (
        f"Ты выбрал тариф: {label}\n\n"
        f"Переведи {price}₽ на карту Сбербанк 👇\n"
        "После перевода нажми «Я оплатил» и жди подтверждения от администратора."
    )


PAYMENT_SENT_TO_USER = (
    "✅ Отлично! Отправил информацию администратору.\n"
    "Дождись подтверждения оплаты 🙌"
)

PAYMENT_CONFIRMED_USER = (
    "🎉 Оплата подтверждена! Дни начислены.\n\n"
    f"Спасибо, что играешь на {SERVER_NAME} — мы ценим каждого игрока ❤️"
)

RULES_MENU = "📜 Какие правила посмотреть?"

RULES_SERVER = (
    "📜 Правила сервера\n\n"
    "🔹 Не спамь в чат\n"
    "🔹 Уважай других игроков, без оскорблений\n"
    "🔹 Не читерь и не используй запрещённые моды/чит-клиенты\n"
    "🔹 Не крашь чужие постройки без разрешения\n"
    "🔹 Не убивай других игроков без обоюдного согласия или веской причины\n\n"
    "⚠️ За нарушение общения: сначала предупреждение, потом временный мут.\n"
    "⚠️ За читерство, крашеры, убийства без причины — бан навсегда, дни сгорают.\n"
    "Разбан можно купить — пиши администратору в личку."
)

RULES_TGK = (
    "📜 Правила общения в телеграм-канале\n\n"
    "🔹 Не спамь\n"
    "🔹 Не оскорбляй других участников\n"
    "🔹 Никакой рекламы без разрешения\n"
    "🔹 Уважай администрацию и других игроков\n\n"
    "⚠️ За нарушение: предупреждение → временный мут.\n"
    "За серьёзные нарушения — бан."
)

REPORT_MENU = "🚨 Куда пожаловаться?"

REPORT_FORM_SERVER = (
    "Напиши жалобу в формате:\n\n"
    "1️⃣ Ник нарушителя\n"
    "2️⃣ Нарушение\n"
    "3️⃣ Доказательства (необязательно)\n\n"
    "Пример:\n"
    "Steve228\n"
    "Читерил, летал без крыльев\n"
    "видео: https://..."
)

REPORT_FORM_TGK = (
    "Напиши жалобу в формате:\n\n"
    "1️⃣ Юзернейм нарушителя\n"
    "2️⃣ Нарушение\n"
    "3️⃣ Доказательства (необязательно)\n\n"
    "Пример:\n"
    "@someuser\n"
    "Оскорблял других в чате\n"
    "скриншот приложен"
)

REPORT_SENT_USER = "✅ Жалоба отправлена администратору."

REPORT_UNDER_REVIEW_USER = "🔎 Жалоба рассматривается, дождись итогов."


def report_verdict_user(verdict: str) -> str:
    return f"📋 Итоги жалобы:\n\n{verdict}"


ADMIN_ASK_VERDICT = "Напиши итог рассмотрения жалобы — это сообщение отправится игроку как есть:"

ADMIN_VERDICT_SENT = "✅ Итоги отправлены пользователю."

NOT_REGISTERED = "Сначала нажми /start и зарегистрируйся 🙂"

# --- Тексты для админ-команд ---

ADMIN_USAGE_BAN = "Использование: /ban ник [причина]"
ADMIN_USAGE_UNBAN = "Использование: /unban ник"
ADMIN_USAGE_EXTEND = "Использование: /extend ник количество_дней"
ADMIN_USAGE_REDUCE = "Использование: /reduce ник количество_дней"
ADMIN_USAGE_INFO = "Использование: /info ник"

ADMIN_USER_NOT_FOUND = "❌ Игрок с таким ником не найден."


def admin_ban_done(mc_nick: str, reason: str) -> str:
    r = f"\nПричина: {reason}" if reason else ""
    return f"⛔ Игрок {mc_nick} забанен, дни обнулены.{r}\nНе забудь убрать его из вайтлиста."


def user_banned_notice(reason: str) -> str:
    r = f"\nПричина: {reason}" if reason else ""
    return f"⛔ Тебя забанили на сервере.{r}\n\nПо вопросам разбана — пиши администратору в личку."


def admin_unban_done(mc_nick: str) -> str:
    return f"✅ Игрок {mc_nick} разбанен. Доступ пока не оплачен — напомни оплатить."


USER_UNBANNED_NOTICE = "✅ Тебя разбанили! Оплати доступ, чтобы снова играть 🙌"


def admin_extend_done(mc_nick: str, days: int, new_until: str) -> str:
    return f"✅ Игроку {mc_nick} добавлено {days} дн. Доступ до: {new_until}"


def admin_reduce_done(mc_nick: str, days: int, new_until: str) -> str:
    return f"✅ У игрока {mc_nick} убавлено {days} дн. Доступ до: {new_until}"


def user_days_changed_notice(days: int, added: bool) -> str:
    word = "начислено" if added else "списано"
    return f"ℹ️ Администратор изменил твой доступ: {word} {abs(days)} дн."


def admin_info_text(user, days: int, hours: int, expired: bool, offset_hours: float) -> str:
    reg_line = f"Зарегистрирован: {timeutils.fmt_iso(user['created_at'], offset_hours)}\n" if user["created_at"] else ""
    left_line = "истёк" if expired else days_hours_line(days, hours, expired)
    tz_line = f"Часовой пояс игрока: UTC{'+' if offset_hours >= 0 else ''}{offset_hours:g}" + (
        "" if user["utc_offset"] is not None else " (по умолчанию, МСК)"
    )
    return (
        f"👤 Профиль игрока\n\n"
        f"ФИ: {user['full_name']}\n"
        f"Ник: {user['mc_nick']}\n"
        f"Telegram id: {user['user_id']}\n"
        f"Статус: {status_ru(user['status'])}\n"
        f"{reg_line}"
        f"Осталось доступа: {left_line}\n"
        f"{tz_line}"
    )


def admin_players_list(users_with_time) -> str:
    """users_with_time — список кортежей (user, days, hours, expired)"""
    if not users_with_time:
        return "Пока никто не зарегистрирован."
    lines = ["📋 Все игроки:\n"]
    for u, days, hours, expired in users_with_time:
        left = days_hours_line(days, hours, expired) if u["status"] == "approved" else "—"
        lines.append(f"• {u['mc_nick']} — {status_ru(u['status'])}, осталось: {left}")
    return "\n".join(lines)
