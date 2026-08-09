import datetime
import aiosqlite

from config import DB_PATH

# status пользователя: pending / approved / rejected / banned


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                mc_nick TEXT,
                status TEXT DEFAULT 'pending',
                access_until TEXT,
                notified_soon INTEGER DEFAULT 0,
                notified_expired INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tariff TEXT,
                price INTEGER,
                days INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER,
                kind TEXT,
                content TEXT,
                status TEXT DEFAULT 'pending',
                verdict TEXT,
                created_at TEXT
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()


async def create_pending_user(user_id: int, full_name: str, mc_nick: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO users (user_id, full_name, mc_nick, status)
               VALUES (?, ?, ?, 'pending')
               ON CONFLICT(user_id) DO UPDATE SET
                 full_name=excluded.full_name,
                 mc_nick=excluded.mc_nick,
                 status='pending'""",
            (user_id, full_name, mc_nick),
        )
        await db.commit()


async def set_user_status(user_id: int, status: str, access_until: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if access_until is not None:
            await db.execute(
                "UPDATE users SET status=?, access_until=?, notified_soon=0, notified_expired=0 WHERE user_id=?",
                (status, access_until, user_id),
            )
        else:
            await db.execute("UPDATE users SET status=? WHERE user_id=?", (status, user_id))
        await db.commit()


async def extend_access(user_id: int, days: int):
    user = await get_user(user_id)
    now = datetime.datetime.now()
    if user and user["access_until"]:
        current = datetime.datetime.fromisoformat(user["access_until"])
        base = current if current > now else now
    else:
        base = now
    new_until = base + datetime.timedelta(days=days)
    await set_user_status(user_id, "approved", new_until.isoformat())
    return new_until


async def mark_notified(user_id: int, field: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field}=1 WHERE user_id=?", (user_id,))
        await db.commit()


async def get_active_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE status='approved'")
        return await cur.fetchall()


async def create_payment(user_id: int, tariff: str, price: int, days: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO payments (user_id, tariff, price, days, status, created_at) VALUES (?, ?, ?, ?, 'pending', ?)",
            (user_id, tariff, price, days, datetime.datetime.now().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def get_payment(payment_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM payments WHERE id=?", (payment_id,))
        return await cur.fetchone()


async def set_payment_status(payment_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
        await db.commit()


async def create_report(reporter_id: int, kind: str, content: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO reports (reporter_id, kind, content, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (reporter_id, kind, content, datetime.datetime.now().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def get_report(report_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM reports WHERE id=?", (report_id,))
        return await cur.fetchone()


async def set_report_verdict(report_id: int, verdict: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE reports SET status='resolved', verdict=? WHERE id=?", (verdict, report_id)
        )
        await db.commit()
