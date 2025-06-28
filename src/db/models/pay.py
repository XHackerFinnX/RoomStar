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
    