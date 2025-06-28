import base64
import json
from zoneinfo import ZoneInfo
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File, Form
from pydantic import BaseModel
from db.models.user import add_basket, get_product_shop, get_saved_basket, save_basket, status_basket_user_expectation
from db.models.pay import add_proofs
from log.log import setup_logger
from random import randint, shuffle
from werkzeug.utils import secure_filename
from auth.telegram_auth import get_verified_user
from datetime import datetime

router = APIRouter(
    prefix="",
    tags=["Shop"]
)

templates = Jinja2Templates(directory="templates")
logger = setup_logger("Shop")
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

class UserRequest(BaseModel):
    user_id: int
    
class UserBasket(BaseModel):
    user_id: int
    list_products: list
    total_sum_rub: float
    total_sum_star: int
    
class UserPay(BaseModel):
    user_id: int
    proof: UploadFile = File(...)

@router.get("/shop", response_class=HTMLResponse)
async def main_basic(request: Request):
    return templates.TemplateResponse("shop.html", {"request": request})

@router.post("/api/get-products")
async def get_products(user_data: dict = Depends(get_verified_user)):
    products = await get_product_shop()
    
    return {"products": products}

@router.post("/api/add-busket-user")
async def add_busket_user(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        digits = list(str(user_id))
        shuffle(digits)
        basket_id = int(''.join(digits)) + randint(1_000, 100_000)
        await add_basket(basket_id, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")
    
@router.post("/api/save-busket-user")
async def save_busket_user(request: UserBasket, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        await save_basket(
            user_id=request.user_id,
            list_products=request.list_products,
            total_sum_rub=request.total_sum_rub,
            total_sum_star=request.total_sum_star
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")

@router.post("/api/get-busket-user")
async def get_busket_user(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        basket_user = await get_saved_basket(request.user_id)
        if basket_user['product_list'] is None:
            basket_user = {
                'list_products': [],
                'total_sum_rub': basket_user['total_sum_rub'],
                'total_sum_star': basket_user['total_sum_star']
            }
        else:
            basket_user = {
                'list_products': json.loads(basket_user['product_list']),
                'total_sum_rub': basket_user['total_sum_rub'],
                'total_sum_star': basket_user['total_sum_star']
            }

        return basket_user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")

@router.post("/api/expectation-basket-user")
async def expectation_basket_user(request: UserRequest, user_data: dict = Depends(get_verified_user)):
    user_id = user_data.user.id
    if user_id == request.user_id:
        await status_basket_user_expectation(request.user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")
    
    
@router.post("/api/upload-proof")
async def upload_proof(
    user_id: str = Form(...),                     
    proof: UploadFile = File(...),               
    user_data: dict = Depends(get_verified_user)
):
    if str(user_id) != str(user_data.user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid initData")

    content = await proof.read()
    filename = secure_filename(proof.filename)
    date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)

    await add_proofs(int(user_id), filename, content, date)

    return {"status": "success"}