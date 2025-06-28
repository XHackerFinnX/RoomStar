import asyncio
import json
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from io import BytesIO
from config import config
from zoneinfo import ZoneInfo
from log.log import setup_logger
from db.models.user import select_user_proof_data, status_basket_user_expectation

bot = Bot(
    config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Message")

async def message_group_proof(user_id: int, filename: str, content: bytes, date):
    GROUP_CHAT_ID = config.ADMIN_GROUP_ID.get_secret_value()
    await asyncio.sleep(3)

    user_data = await select_user_proof_data(user_id)
    if not user_data:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"❌ Не удалось найти данные пользователя: {user_id}")
        return

    user = user_data[0]
    
    try:
        products = json.loads(user["product_list"])
    except Exception as e:
        products = []
        print("Ошибка парсинга product_list:", e)

    product_lines = ""
    for idx, item in enumerate(products, 1):
        product_id, name, count = item
        product_lines += f"{idx}. <b>{name}</b> — <code>{count} шт.</code>\n"

    caption = (
        f"<b>🧾 Новая заявка на подтверждение оплаты</b>\n\n"
        f"<b>👤 Пользователь:</b> <a href='tg://user?id={user_id}'>{user['name']}</a> ({user['tgname']})\n"
        f"<b>🛍️ Покупки:</b>\n{product_lines}\n"
        f"<b>💳 Сумма к оплате:</b> {user['total_sum_rub']} ₽\n"
        f"<b>⭐ Кол-во звёзд:</b> {user['total_sum_star']}⭐\n"
        f"<b>📅 Дата:</b> {date.strftime('%d.%m.%Y %H:%M')}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])

    input_file = BufferedInputFile(file=content, filename=filename)
    ext = filename.lower().split('.')[-1]

    if ext in ["jpg", "jpeg", "png", "gif"]:
        await bot.send_photo(chat_id=GROUP_CHAT_ID, photo=input_file, caption=caption, reply_markup=keyboard)
    elif ext == "pdf":
        await bot.send_document(chat_id=GROUP_CHAT_ID, document=input_file, caption=caption, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"⚠️ Неподдерживаемый тип файла от {user_id}: {filename}")
        
    await status_basket_user_expectation(user_id)