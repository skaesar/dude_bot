from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import get_or_create_user, get_history, save_message
from gemma import ask_gemma
from keyboards import retry_keyboard
from logger import logger

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, pool):
    await get_or_create_user(pool, message.from_user)
    logger.info(f"/start от {message.from_user.id}")
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я твой ИИ-ассистент. Просто напиши мне что-нибудь.\n\n"
        "/help — помощь\n"
        "/history — последние сообщения"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    logger.info(f"/help от {message.from_user.id}")
    await message.answer(
        "🤖 <b>Как пользоваться ботом:</b>\n\n"
        "• Просто напиши любое сообщение\n"
        "• Нажми 🔄 <b>Ещё раз</b> чтобы перегенерировать ответ\n"
        "• /history — посмотреть историю\n"
    )

@router.message(Command("history"))
async def cmd_history(message: Message, pool):
    logger.info(f"/history от {message.from_user.id}")
    history = await get_history(pool, message.from_user.id)

    if not history:
        await message.answer("История пуста.")
        return

    text = "📜 <b>Последние сообщения:</b>\n\n"
    for msg in history:
        icon = "👤" if msg["role"] == "user" else "🤖"
        text += f"{icon} {msg['content'][:100]}\n\n"

    await message.answer(text)

@router.message(F.text)
async def handle_message(message: Message, pool):
    user_id = message.from_user.id
    text = message.text

    logger.info(f"Сообщение от {user_id}: {text[:50]}")
    await get_or_create_user(pool, message.from_user)
    await save_message(pool, user_id, "user", text)

    thinking = await message.answer("⏳ Генерирую ответ...")
    history = await get_history(pool, user_id)
    reply = await ask_gemma(history, text)

    await save_message(pool, user_id, "assistant", reply)
    await thinking.delete()
    await message.answer(reply, reply_markup=retry_keyboard())

@router.callback_query(F.data == "retry")
async def handle_retry(callback: CallbackQuery, pool):
    user_id = callback.from_user.id
    logger.info(f"Retry от {user_id}")

    history = await get_history(pool, user_id)
    last_user_msg = next(
        (m["content"] for m in reversed(history) if m["role"] == "user"),
        None
    )

    if not last_user_msg:
        await callback.answer("Нет предыдущего запроса.", show_alert=True)
        return

    await callback.answer("🔄 Генерирую заново...")
    thinking = await callback.message.answer("⏳ Генерирую ответ...")

    fresh_history = history[:-1]
    reply = await ask_gemma(fresh_history, last_user_msg)

    await save_message(pool, user_id, "assistant", reply)
    await thinking.delete()
    await callback.message.answer(reply, reply_markup=retry_keyboard())