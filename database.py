import aiosqlite
import math
from datetime import date, datetime

from config import DB_PATH, SERVER_DAILY_COST


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                mc_nick TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                registered_at TEXT,
                created_at TEXT NOT NULL,
                warned_day6 INTEGER NOT NULL DEFAULT 0,
                mentioned_day7 INTEGER NOT NULL DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                source TEXT NOT NULL,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS yoomoney_ops (
                operation_id TEXT PRIMARY KEY
            )
        """)
        await db.commit()


def _today():
    return date.today().isoformat()


def _now():
    return datetime.now().isoformat()


# ---------- Players ----------

async def add_pending_player(tg_id: int, username: str, full_name: str, mc_nick: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO players (tg_id, username, full_name, mc_nick, status, created_at) "
            "VALUES (?, ?, ?, ?, 'pending', ?)",
            (tg_id, username, full_name, mc_nick, _now()),
        )
        await db.commit()


async def add_confirmed_player(tg_id: int, username: str, full_name: str, mc_nick: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO players (tg_id, username, full_name, mc_nick, status, created_at, registered_at) "
            "VALUES (?, ?, ?, ?, 'confirmed', ?, ?)",
            (tg_id, username, full_name, mc_nick, _now(), _today()),
        )
        await db.commit()


async def get_player(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM players WHERE tg_id = ?", (tg_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_player_by_id(player_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def confirm_player(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE players SET status = 'confirmed', registered_at = ? WHERE tg_id = ?",
            (_today(), tg_id),
        )
        await db.commit()


async def reject_player(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE players SET status = 'rejected' WHERE tg_id = ?", (tg_id,))
        await db.commit()


async def ban_player(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE players SET status = 'banned' WHERE tg_id = ?", (tg_id,))
        await db.commit()


async def unban_player(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE players SET status = 'confirmed' WHERE tg_id = ?", (tg_id,))
        await db.commit()


async def remove_player(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM players WHERE tg_id = ?", (tg_id,))
        await db.commit()


async def get_all_confirmed_players():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM players WHERE status = 'confirmed'")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def set_debt_flags(tg_id: int, warned_day6: int = None, mentioned_day7: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if warned_day6 is not None:
            await db.execute("UPDATE players SET warned_day6 = ? WHERE tg_id = ?", (warned_day6, tg_id))
        if mentioned_day7 is not None:
            await db.execute("UPDATE players SET mentioned_day7 = ? WHERE tg_id = ?", (mentioned_day7, tg_id))
        await db.commit()


# ---------- Settings (used for manual player-count override) ----------

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await db.commit()


async def get_setting(key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cur.fetchone()
        return row[0] if row else None


async def get_active_player_count() -> int:
    override = await get_setting("player_count_override")
    if override:
        return max(1, int(override))
    players = await get_all_confirmed_players()
    return max(1, len(players))


async def get_daily_rate() -> float:
    count = await get_active_player_count()
    return SERVER_DAILY_COST / count


# ---------- Payments ----------

async def add_payment(player_id: int, amount: float, source: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO payments (player_id, amount, date, source) VALUES (?, ?, ?, ?)",
            (player_id, amount, _today(), source),
        )
        await db.commit()


async def get_total_paid(player_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE player_id = ?", (player_id,))
        row = await cur.fetchone()
        return row[0] or 0.0


async def get_total_server_paid() -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
        row = await cur.fetchone()
        return row[0] or 0.0


# ---------- Stats ----------

async def get_player_stats(tg_id: int):
    """Считает оплаченные дни и долг игрока на лету, по текущему тарифу."""
    player = await get_player(tg_id)
    if not player:
        return None

    total_paid = await get_total_paid(player["id"])
    daily_rate = await get_daily_rate()

    paid_days = math.floor(total_paid / daily_rate) if daily_rate > 0 else 0
    remainder = round(total_paid - paid_days * daily_rate, 2)

    debt_days = 0
    if player["registered_at"]:
        reg_date = date.fromisoformat(player["registered_at"])
        days_since_reg = (date.today() - reg_date).days
        debt_days = max(0, days_since_reg - paid_days)

    return {
        "player": player,
        "total_paid": total_paid,
        "daily_rate": round(daily_rate, 2),
        "paid_days": paid_days,
        "remainder": remainder,
        "debt_days": debt_days,
    }


# ---------- YooMoney dedup ----------

async def is_operation_processed(operation_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM yoomoney_ops WHERE operation_id = ?", (operation_id,))
        row = await cur.fetchone()
        return row is not None


async def mark_operation_processed(operation_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO yoomoney_ops (operation_id) VALUES (?)", (operation_id,)
        )
        await db.commit()
