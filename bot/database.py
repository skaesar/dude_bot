import asyncpg
from config import config

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

async def get_or_create_user(pool, user):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING
        """, user.id, user.username, user.first_name)

async def get_history(pool, user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT role, content FROM messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """, user_id, config.history_limit)
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

async def save_message(pool, user_id, role, content):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO messages (user_id, role, content)
            VALUES ($1, $2, $3)
        """, user_id, role, content)