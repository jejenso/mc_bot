import datetime

# Если игрок не поделился геолокацией — показываем время по МСК
DEFAULT_OFFSET_HOURS = 3.0


def now() -> datetime.datetime:
    """'Внутреннее' время — то, что видит сервер (UTC на Railway). Используется для расчётов и хранения в базе."""
    return datetime.datetime.now()


def effective_offset(user) -> float:
    """Часовой пояс конкретного игрока (если делился геолокацией), иначе МСК."""
    if user is not None and user["utc_offset"] is not None:
        return user["utc_offset"]
    return DEFAULT_OFFSET_HOURS


def fmt(dt: datetime.datetime, offset_hours: float = DEFAULT_OFFSET_HOURS) -> str:
    """Например: 09.08.2026 19:46 (UTC+6)"""
    local = dt + datetime.timedelta(hours=offset_hours)
    sign = "+" if offset_hours >= 0 else ""
    offset_str = f"{offset_hours:g}"
    return f"{local.strftime('%d.%m.%Y %H:%M')} (UTC{sign}{offset_str})"


def fmt_iso(iso_str: str | None, offset_hours: float = DEFAULT_OFFSET_HOURS) -> str:
    if not iso_str:
        return "—"
    return fmt(datetime.datetime.fromisoformat(iso_str), offset_hours)


def time_left(access_until_str: str | None):
    """Возвращает (days, hours, expired). От часового пояса не зависит — это просто разница во времени."""
    if not access_until_str:
        return 0, 0, True
    until = datetime.datetime.fromisoformat(access_until_str)
    delta = (until - now()).total_seconds()
    if delta <= 0:
        return 0, 0, True
    days = int(delta // 86400)
    hours = int((delta % 86400) // 3600)
    return days, hours, False
