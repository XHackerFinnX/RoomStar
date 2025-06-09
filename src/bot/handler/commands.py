from aiogram import Router, html, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.keyboard.inline import markup_start
from bot.tg_name import telegram_name_users
from bot.text import HELLO_START_TEXT, MENU_TEXT
from db.models.user import add_user, add_wheel_user
from log.log import setup_logger
from zoneinfo import ZoneInfo

router = Router()
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Commands")

@router.message(CommandStart())
async def start_bot(message: Message, bot: Bot):
    
    user_data = await telegram_name_users(message)
    user_id = user_data['id_user']
    user_tgname = user_data['uname']
    user_name = user_data['fname']
    photos = await bot.get_user_profile_photos(user_id=user_id, limit=1)
    if photos.total_count == 0:
        user_photo = None
    else:
        file_id = photos.photos[0][-1].file_id
        file = await bot.get_file(file_id)
        file_data = await bot.download_file(file.file_path)
        user_photo = file_data.read()
        
    await add_user(
        user_id,
        user_name,
        user_tgname,
        user_photo
    )
    
    await add_wheel_user(user_id)
        
    logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Запустил команду /start без параметров")
    await message.answer(
        text=f"{HELLO_START_TEXT}{html.bold(user_name)}!{MENU_TEXT}",
        reply_markup=markup_start
    )