import asyncpg
import os
from config import DATABASE_URL

_pool = None

CATEGORIES = ["Darslik", "Sharh", "Kodeks", "Qo'llanma", "Sohaga doir normalar"]

DEFAULT_DIRECTIONS = [
    ("Konstitutsiyaviy huquq", "⚖️"),
    ("Fuqarolik huquqi", "🏛️"),
    ("Oila huquqi", "👨‍👩‍👧"),
    ("Xalqaro huquq", "🌍"),
    ("Jinoyat huquqi", "🔒"),
    ("Ma'muriy huquq", "📋"),
    ("Soliq huquqi", "💰"),
    ("Mehnat huquqi", "👷"),
]


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            ssl="require",
            statement_cache_size=0
        )
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mandatory_channels (
                id SERIAL PRIMARY KEY,
                channel_id TEXT NOT NULL,
                channel_name TEXT,
                channel_link TEXT,
                added_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS directions (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT DEFAULT '📚',
                added_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                direction_id INTEGER REFERENCES directions(id) ON DELETE SET NULL,
                category TEXT,
                subject TEXT,
                file_id TEXT NOT NULL,
                added_by BIGINT,
                added_at TIMESTAMP DEFAULT NOW(),
                download_count INTEGER DEFAULT 0
            )
        """)
        # Seed default directions
        for name, emoji in DEFAULT_DIRECTIONS:
            await conn.execute(
                "INSERT INTO directions (name, emoji) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
                name, emoji
            )


# ─── USERS ────────────────────────────────────────────────────────────────────

async def add_user(user_id: int, username: str, full_name: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING",
            user_id, username, full_name
        )


async def get_all_users():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
        return [r["user_id"] for r in rows]


async def get_users_count():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")


async def get_new_users_today():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE joined_at::date = CURRENT_DATE"
        )


async def get_new_users_week():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE joined_at >= NOW() - INTERVAL '7 days'"
        )


# ─── MANDATORY CHANNELS ───────────────────────────────────────────────────────

async def add_mandatory_channel(channel_id: str, channel_name: str, channel_link: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO mandatory_channels (channel_id, channel_name, channel_link) VALUES ($1, $2, $3)",
            channel_id, channel_name, channel_link
        )


async def remove_mandatory_channel(channel_id: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM mandatory_channels WHERE channel_id = $1", channel_id)


async def get_mandatory_channels():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT channel_id, channel_name, channel_link FROM mandatory_channels")
        return [{"id": r["channel_id"], "name": r["channel_name"], "link": r["channel_link"]} for r in rows]


# ─── DIRECTIONS ───────────────────────────────────────────────────────────────

async def add_direction(name: str, emoji: str = "📚"):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO directions (name, emoji) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
            name, emoji
        )


async def get_all_directions():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, emoji FROM directions ORDER BY name")
        return [{"id": r["id"], "name": r["name"], "emoji": r["emoji"]} for r in rows]


async def delete_direction(direction_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM directions WHERE id = $1", direction_id)


# ─── BOOKS ────────────────────────────────────────────────────────────────────

async def add_book(title, author, year, direction_id, category, subject, file_id, added_by):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO books (title, author, year, direction_id, category, subject, file_id, added_by)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            title, author, year, direction_id, category, subject, file_id, added_by
        )


async def get_books_by_direction(direction_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT b.id, b.title, b.author, b.year, b.category, b.subject, b.download_count, d.name as dir_name
               FROM books b JOIN directions d ON b.direction_id = d.id
               WHERE b.direction_id = $1 ORDER BY b.title""",
            direction_id
        )
        return [{"id": r["id"], "title": r["title"], "author": r["author"], "year": r["year"],
                 "category": r["category"], "subject": r["subject"], "downloads": r["download_count"],
                 "direction": r["dir_name"]} for r in rows]


async def get_book_by_id(book_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        r = await conn.fetchrow(
            """SELECT b.id, b.title, b.author, b.year, b.category, b.subject,
                      b.file_id, b.download_count, d.name as dir_name
               FROM books b JOIN directions d ON b.direction_id = d.id
               WHERE b.id = $1""",
            book_id
        )
        if r:
            return {"id": r["id"], "title": r["title"], "author": r["author"], "year": r["year"],
                    "category": r["category"], "subject": r["subject"], "file_id": r["file_id"],
                    "downloads": r["download_count"], "direction": r["dir_name"]}
        return None


async def search_books(query: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        q = f"%{query}%"
        rows = await conn.fetch(
            """SELECT b.id, b.title, b.author, b.year, b.category, b.subject, b.download_count, d.name as dir_name
               FROM books b JOIN directions d ON b.direction_id = d.id
               WHERE b.title ILIKE $1 OR b.author ILIKE $2
               ORDER BY b.title LIMIT 20""",
            q, q
        )
        return [{"id": r["id"], "title": r["title"], "author": r["author"], "year": r["year"],
                 "category": r["category"], "subject": r["subject"], "downloads": r["download_count"],
                 "direction": r["dir_name"]} for r in rows]


async def increment_download(book_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE books SET download_count = download_count + 1 WHERE id = $1", book_id)


async def get_books_count():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM books")


async def get_books_stats_by_direction():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT d.name, d.emoji, COUNT(b.id) as book_count
               FROM directions d LEFT JOIN books b ON b.direction_id = d.id
               GROUP BY d.id, d.name, d.emoji ORDER BY book_count DESC"""
        )
        return [{"direction": r["name"], "emoji": r["emoji"], "count": r["book_count"]} for r in rows]


async def delete_book(book_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM books WHERE id = $1", book_id)
