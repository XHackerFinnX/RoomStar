from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from datetime import datetime
from zoneinfo import ZoneInfo
from log.log import setup_logger
from config import config

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Message")

bot = Bot(
    config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

async def bot_username(user_id):
    user_data = await bot.get_chat(user_id)
    user_name = '@' + str(user_data.username)
    user_fname = str(user_data.first_name)
    user_lname = str(user_data.last_name)
    
    return {
        "user_id": user_id,
        "user_name": user_name,
        "user_fname": user_fname,
        "user_lname": user_lname
    }

async def notifications_wheel_free_attempt(user_id):
    user_data = await bot_username(user_id)
    await bot.send_message(
        chat_id=user_data['user_id'],
        text=f"👋🏻 Привет, {user_data['user_fname']}!\n\n🔔 Ты получил 3 бесплатные попытки на колесе удачи.\n🎯 Используй их, чтобы выиграть ⭐️ звезды!"
    )