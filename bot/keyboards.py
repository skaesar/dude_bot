from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def retry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="retry")]
    ])