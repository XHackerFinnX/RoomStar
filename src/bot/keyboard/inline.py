from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo, InlineKeyboardButton
from config import config

markup_start = InlineKeyboardBuilder().add(
    InlineKeyboardButton(
        text="⭐ Открыть приложение",
        web_app=WebAppInfo(url=config.WEBAPP_URL)
    )
).as_markup()