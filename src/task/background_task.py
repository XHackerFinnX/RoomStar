import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from log.log import setup_logger
from bot.handler.notifications import notifications_wheel_free_attempt
from db.models.user import update_status_and_attempt_user_wheel

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("notifications")

async def notifications_wheel_user_attempt(user_id: int):
    logger.info(f'Пользователь {user_id} истратил все попытки и через 30 мин ждет уведомления')
    await asyncio.sleep(1800)
    logger.info(f'Пользователь {user_id} возобновил попытки')
    await update_status_and_attempt_user_wheel(user_id)
    await notifications_wheel_free_attempt(user_id)
    