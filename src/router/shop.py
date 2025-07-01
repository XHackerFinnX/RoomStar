import base64
import json
from zoneinfo import ZoneInfo
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File, Form, BackgroundTasks, Query
from pydantic import BaseModel
from db.models.user import add_basket, get_product_shop, get_saved_basket, save_basket
from db.models.pay import add_proofs, check_payment_status, check_secret_id_user, delete_basket_checking, update_basket_secret_id, get_basket_id, update_status_checking_pay
from log.log import setup_logger
from random import randint, shuffle
from werkzeug.utils import secure_filename
from auth.telegram_auth import get_verified_user
from datetime import datetime, timedelta
from bot.handler.message import message_group_proof
from auth.secret_basket import generate_secret_id

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

class UserTypePay(BaseModel):
    user_id: int
    type_pay: str
    
class StatusCheckRequest(BaseModel):
    user_id: str
    secret_id: str

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
        # await status_basket_user_expectation(request.user_id)
        return True
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid initData")
    
    
@router.post("/api/upload-proof")
async def upload_proof(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),                     
    proof: UploadFile = File(...),
    secret_id: str = Form(...),
    basket_id: str = Form(...),
    user_data: dict = Depends(get_verified_user),
):
    if str(user_id) != str(user_data.user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid initData")

    try:
        content = await proof.read()
        filename = secure_filename(proof.filename)
        date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)

        await add_proofs(int(user_id), filename, content, date)
        background_tasks.add_task(message_group_proof, int(user_id), filename, content, date)
        await update_status_checking_pay(int(user_id), int(basket_id), secret_id, 'Проверяется', False)
        return {"status": "success"}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Data")
    

@router.post("/api/get-basket-id")
async def upload_proof(request: UserTypePay, user_data: dict = Depends(get_verified_user)):
    if str(request.user_id) != str(user_data.user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid initData")

    try:
        basket = await get_basket_id(request.user_id)
        basket_id = basket['basket_id']
        secret_id = generate_secret_id(basket_id)
        date_time_10plus = datetime.now(MOSCOW_TZ).replace(tzinfo=None) + timedelta(minutes=10)
        await update_basket_secret_id(request.user_id, secret_id, 'Ожидание чека', request.type_pay, date_time_10plus)

        return {
            "basket_id": basket_id,
            "secret_id": secret_id
        }
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Data")


@router.get("/checking_payment")
async def checking_payment(
    request: Request,
    user_id: str = Query(...),
    basket_id: str = Query(...),
    type_pay: str = Query(...),
    secret_id: str = Query(...)
):
    try:
        data_pay = await check_secret_id_user(secret_id, int(user_id), int(basket_id), type_pay)
        now = datetime.now(MOSCOW_TZ).replace(tzinfo=None)
        future = data_pay['time_status']
        status_p = data_pay['status_pay']
        seconds_until = int((future - now).total_seconds())
        
        if status_p != 'Проверяется':
            if seconds_until < 0:
                await update_status_checking_pay(int(user_id), int(basket_id), secret_id, 'Время вышло', True)
                return RedirectResponse(url="/")
        
        return templates.TemplateResponse("checking_receipt.html", {
            "request": request,
            "user_id": data_pay['user_id'],
            "basket_id": data_pay['basket_id'],
            "secret_id": secret_id,
            "type_pay": data_pay['type_payments'],
            "status_pay": data_pay['status_pay'],
            "time_date": seconds_until,
            "total_sum_rub": data_pay['total_sum_rub'],
            "total_sum_star": data_pay['total_sum_star']
        })

    except Exception as e:
        print(f"Ошибка /checking_payment: {e}")
        return RedirectResponse(url="/error")
    
@router.post("/api/check-status")
async def check_status_pay(
    request_data: StatusCheckRequest,
    user_data: dict = Depends(get_verified_user)
):
    if str(user_data.user.id) != str(request_data.user_id):
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied"}
        )
    logger.info(f"Пользователь {request_data.user_id} ждёт получение звёзд")
    status = await check_payment_status(request_data.secret_id, int(request_data.user_id))
    return {"status": status['status_pay']}

@router.delete("/api/delete_checking_payment")
async def delete_checking_payment(basket_id: str = Query(...), user_data: dict = Depends(get_verified_user)):
    try:
        user_id = user_data.user.id
        await delete_basket_checking(int(user_id), int(basket_id))
    except:
        return RedirectResponse(url="/error")