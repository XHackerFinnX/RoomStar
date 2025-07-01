import json
from db.database import DataBase

Database = DataBase()

async def add_proofs(user_id: int, filename: str, file_data: bytes, date):
    query = """
    INSERT INTO proofs (user_id, filename, file_data, date)
    VALUES ($1, $2, $3, $4)
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id, filename, file_data, date)
    except Exception as error:
        print(f"Ошибка добавление подверждения оплаты пользователя user_id {user_id} в БД: {error}")
        
        
async def get_basket_id(user_id: int):
    query = """
    SELECT basket_id
    FROM basket
    WHERE user_id = $1 AND status = false
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            basket_user = await conn.fetchrow(query, user_id)
            return basket_user
    except Exception as error:
        print(f"Ошибка в получении basket_id пользователя {user_id} из БД: {error}")
        
async def get_basket_all_bot_message(user_id: int):
    query = """
    SELECT * FROM basket 
    WHERE user_id = $1 AND status = false AND status_pay = 'Проверяется'
    """

    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, user_id)

        if result is None:
            return None

        return dict(result)

    except Exception as error:
        print(f"Ошибка при получении корзины пользователя: {error}")
        return None

async def get_basket_all_start_message(user_id: int):
    query = """
    SELECT * FROM basket 
    WHERE user_id = $1 AND status = false AND (status_pay = 'Проверяется' OR status_pay = 'Ожидание чека')
    """

    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, user_id)

        if result is None:
            return None

        return dict(result)

    except Exception as error:
        print(f"Ошибка при получении корзины пользователя: {error}")
        return None
        
async def update_basket_secret_id(user_id: int, secret_id: str, status_pay: str, type_pay: str, time_status):
    query = """
    UPDATE basket
    SET secret_id = $1, time_status = $2, status_pay = $3, type_payments = $4
    WHERE user_id = $5 AND status = false
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, secret_id, time_status, status_pay, type_pay, user_id)
    except Exception as error:
        print(f"Ошибка обновления secret_id корзины пользователя {user_id} в БД: {error}")


async def check_secret_id_user(secret_id: str, user_id: int, basket_id: int, type_pay: str):
    query = """
    SELECT user_id, basket_id, type_payments, status_pay, time_status, total_sum_rub, total_sum_star
    FROM basket
    WHERE secret_id = $1 AND type_payments = $2 AND user_id = $3 AND basket_id = $4
    """

    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, secret_id, type_pay, user_id, basket_id)
        if result:
            return dict(result)
        else:
            raise Exception
    except Exception as error:
        print(f"Ошибка при проверке secret_id: {error}")
        raise error

async def update_status_checking_pay(user_id: int, basket_id: int, secret_id: str, status_pay: str, status: bool):
    query = """
    UPDATE basket
    SET status = $1, status_pay = $2
    WHERE secret_id = $3 AND basket_id = $4 AND user_id = $5
    """

    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, status, status_pay, secret_id, basket_id, user_id)
    except Exception as error:
        print(f"Ошибка обновления статуса оплаты корзины пользователя {user_id} в БД: {error}")
    
async def delete_basket_checking(user_id: int, basket_id: int):
    query = "DELETE FROM basket WHERE user_id = $1 AND basket_id = $2 AND status_pay = $3"
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id, basket_id, 'Ожидание чека')
    except Exception as error:
        print(f"Ошибка удаления корзины и отмены оплаты пользователя {user_id} в БД: {error}")


async def check_payment_status(secret_id: str, user_id: int):
    query = """
    SELECT status_pay
    FROM basket
    WHERE secret_id = $1 AND user_id = $2
    """

    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, secret_id, user_id)
        if result:
            return dict(result)
        else:
            raise Exception("Запись не найдена")
    except Exception as error:
        print(f"Ошибка при проверке статуса оплаты: {error}")
        raise error