from typing import Dict
from fastapi import HTTPException, status, Request
from config import config
from init_data_py import InitData
        
async def get_verified_user(request: Request) -> Dict:
    init_data_str = request.headers.get("X-Telegram-InitData")
    if not init_data_str:
        raise HTTPException(status_code=400, detail="Missing X-Telegram-InitData header")

    try:
        init_data = InitData.parse(init_data_str)
        init_data.validate(bot_token=config.BOT_TOKEN.get_secret_value())
        return init_data
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")