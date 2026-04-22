import asyncio
import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers import router
from database import init_db
from menu import set_commands
from logger import logger
from config import config

async def main():
    pool = await asyncpg.create_pool(
        host=config.db.host,
        user=config.db.user,
        password=config.db.password,
        database=config.db.name
    )
    logger.info("Пул соединений с БД открыт")
    await init_db(pool)

    bot = Bot(token=config.tg_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp["pool"] = pool
    dp.include_router(router)

    await set_commands(bot)
    logger.info("Бот запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await pool.close()
        logger.info("Пул соединений с БД закрыт")
        await bot.session.close()
        logger.info("Сессия бота закрыта")

if __name__ == "__main__":
    asyncio.run(main())