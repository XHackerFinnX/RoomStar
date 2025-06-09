import asyncio
from zoneinfo import ZoneInfo
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from log.log import setup_logger
from db.models.user import get_attempt_user_wheel, get_balance_user_wheel, get_win_wheel_user, update_status_notifications_wheel, update_wheel_user
from auth.telegram_auth import get_verified_user
from task.background_task import notifications_wheel_user_attempt

router = APIRouter(
    prefix="",
    tags=["Wheel"]
)

templates = Jinja2Templates(directory="templates")
logger = setup_logger("Wheel")
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

class UserRequest(BaseModel):
    user_id: int
    
class UserWheel(BaseModel):
    user_id: int
    stars: int
    spins: int


@router.get("/wheel", response_class=HTMLResponse)
async def main_wheel(request: Request):
    return templates.TemplateResponse("wheel.html", {"request": request})


@router.post("/api/get_balance_wheel")
async def get_balance_wheel(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        balance = await get_balance_user_wheel(request.user_id)
        return {
            "balance": balance
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")


@router.post("/api/get_free_spins_wheel")
async def get_spins_wheel(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        spins = await get_attempt_user_wheel(request.user_id)
        return {
            "freeSpins": spins
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")

@router.post("/api/update_after_spin")
async def update_after_spin(request: UserWheel, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        if request.spins == 0:
            if await update_status_notifications_wheel(user_id):
                asyncio.create_task(
                    notifications_wheel_user_attempt(user_id)
                )

        await update_wheel_user(
            user_id,
            request.stars,
            request.spins
        )

        return {"status": "ok"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")
    
@router.post("/api/get_prizes_wheel")
async def get_prizes_wheel(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        win = await get_win_wheel_user(request.user_id)
        prizes = [
            {"text": "0 ⭐", "color": "hsl(197 30% 43%)", "win": int(win['stars_win_0']), "amount": 0},
            {"text": "2 ⭐", "color": "hsl(173 58% 39%)", "win": int(win['stars_win_2']), "amount": 2},
            {"text": "5 ⭐", "color": "hsl(43 74% 66%)", "win": int(win['stars_win_5']), "amount": 5},
            {"text": "10 ⭐", "color": "hsl(27 87% 67%)", "win": int(win['stars_win_10']), "amount": 10},
            {"text": "20 ⭐", "color": "hsl(12 76% 61%)", "win": int(win['stars_win_20']), "amount": 20},
            {"text": "50 ⭐", "color": "hsl(350 60% 52%)", "win": int(win['stars_win_50']), "amount": 50},
            {"text": "100 ⭐", "color": "hsl(91 43% 54%)", "win": int(win['stars_win_100']), "amount": 100},
            {"text": "200 ⭐", "color": "hsl(140 36% 74%)", "win": int(win['stars_win_200']), "amount": 200},
        ]
        
        return {"prizes": prizes}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")