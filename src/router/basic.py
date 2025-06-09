import base64
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from db.models.user import get_user_name_photo, get_user_name_tgname
from log.log import setup_logger
from auth.telegram_auth import get_verified_user

router = APIRouter(
    prefix="",
    tags=["Basic"]
)

templates = Jinja2Templates(directory="templates")
logger = setup_logger("Basic")

class UserRequest(BaseModel):
    user_id: int


@router.get("/", response_class=HTMLResponse)
async def main_basic(request: Request):
    return templates.TemplateResponse("basic.html", {"request": request})

@router.get("/error", response_class=HTMLResponse)
async def get_error(request: Request):
    return templates.TemplateResponse("error.html", {"request": request})

@router.post("/api/get_user_info")
async def get_user_info(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        user_data = await get_user_name_photo(request.user_id)
        name = user_data['name']
        photo = user_data['photo']
        photo = base64.b64encode(photo).decode('utf-8') if photo else None

        return {
            "name": name,
            "avatar_base64": photo
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")
    
@router.post("/api/get_username")
async def get_username(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        user_data = await get_user_name_tgname(request.user_id)
        name, tgname = user_data
        
        return {
            "name": name,
            "telegram": tgname
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")