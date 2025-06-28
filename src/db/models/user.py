import json
from db.database import DataBase

Database = DataBase()

async def add_user(
    user_id: int,
    user_name: str,
    user_tgname: str,
    user_photo
):
    
    query = """
    SELECT user_id FROM users 
    WHERE user_id = $1
    """

    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            users = await conn.fetch(query, user_id)
    except Exception as error:
        print(f"Ошибка в получении user_id {user_id} пользователя в БД: {error}")
    
    if not users:
        query = """
        INSERT INTO users (user_id, name, tgname, photo) 
        VALUES ($1, $2, $3, $4)
        """
        
        try:
            pool = await Database.connect()
            async with pool.acquire() as conn:
                await conn.execute(query, user_id, user_name, user_tgname, user_photo)
        except Exception as error:
            print(f"Ошибка добавление пользователя в БД: {error}")
    else:
        query = """
        UPDATE users SET name = $1, tgname = $2, photo = $3 
        WHERE user_id = $4
        """
        
        try:
            pool = await Database.connect()
            async with pool.acquire() as conn:
                await conn.execute(query, user_name, user_tgname, user_photo, user_id)
        except Exception as error:
            print(f"Ошибка при обновлении данных пользователя в БД: {error}")
            return False
        

async def select_user_proof_data(user_id: int):
    query = """
    SELECT 
        u.user_id, u.name, u.tgname,
        b.basket_id, b.product_list, b.total_sum_rub, b.total_sum_star,
        p.date
    FROM proofs AS p
    JOIN users AS u ON u.user_id = p.user_id
    JOIN basket AS b ON b.user_id = p.user_id
    WHERE u.user_id = $1 AND b.status = false
    ORDER BY p.date DESC
    LIMIT 1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            users_data = await conn.fetch(query, user_id)
            return users_data
    except Exception as error:
        print(f"Ошибка в получении данных чека и пользователя {user_id} в БД: {error}")
  
async def add_wheel_user(user_id: int):
    
    query = """
    SELECT user_id FROM wheel_balance 
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            users = await conn.fetch(query, user_id)
    except Exception as error:
        print(f"Ошибка в получении user_id {user_id} колеса пользователя в БД: {error}")
        
    if not users:
        query = """
        INSERT INTO wheel_balance (user_id, stars, wheel_attempt, status_notifications) 
        VALUES ($1, 10, 3, false)
        """
        
        try:
            pool = await Database.connect()
            async with pool.acquire() as conn:
                await conn.execute(query, user_id)
        except Exception as error:
            print(f"Ошибка добавление пользователя колеса в БД: {error}")
            
        query = """
        INSERT INTO wheel_user (user_id, stars_win_0, stars_win_2, stars_win_5, stars_win_10, stars_win_20, stars_win_50, stars_win_100, stars_win_200) 
        VALUES ($1, 80, 50, 30, 10, 3, 1, 0.01, 0.0001)
        """
        
        try:
            pool = await Database.connect()
            async with pool.acquire() as conn:
                await conn.execute(query, user_id)
        except Exception as error:
            print(f"Ошибка добавление пользователя колеса шанс выигрыша в БД: {error}")
        

async def get_user_name_photo(user_id: int):
    
    query = """
    SELECT name, photo FROM users 
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            users = await conn.fetchrow(query, user_id)
            return users
    except Exception as error:
        print(f"Ошибка в получении name и photo пользователя в БД: {error}")
        
        
async def get_user_name_tgname(user_id: int):
    
    query = """
    SELECT name, tgname FROM users 
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            users = await conn.fetchrow(query, user_id)
            return users
    except Exception as error:
        print(f"Ошибка в получении name и tgname пользователя в БД: {error}")
        
        
async def get_product_shop():
    
    query = """
    SELECT product_id, name, stars_price, old_price, new_price, image
    FROM shop
    ORDER BY product_id ASC
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            product = await conn.fetch(query)
            return product
    except Exception as error:
        print(f"Ошибка в получении товаров из БД: {error}")
        
        
async def add_basket(basket_id: int, user_id: int):
    
    query = """
    SELECT user_id 
    FROM basket
    WHERE user_id = $1 AND status = false
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            basket_user = await conn.fetch(query, user_id)
    except Exception as error:
        print(f"Ошибка в получении корзины из БД: {error}")
    
    if not basket_user:
        query = """
        INSERT INTO basket (basket_id, user_id, status) 
        VALUES ($1, $2, false)
        """
        
        try:
            pool = await Database.connect()
            async with pool.acquire() as conn:
                await conn.execute(query, basket_id, user_id)
        except Exception as error:
            print(f"Ошибка создания корзины для пользователя {user_id} в БД: {error}")
            
            
async def save_basket(
    user_id: int,
    list_products: list,
    total_sum_rub: int,
    total_sum_star: int
):
    query = """
    UPDATE basket
    SET product_list = $1,
    total_sum_rub = $2,
    total_sum_star = $3
    WHERE user_id = $4 AND status = false
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, json.dumps(list_products, ensure_ascii=False), total_sum_rub, total_sum_star, user_id)
    except Exception as error:
        print(f"Ошибка обновления корзины для пользователя {user_id} в БД: {error}")


async def get_saved_basket(user_id: int):
    query = """
    SELECT product_list, total_sum_rub, total_sum_star 
    FROM basket
    WHERE user_id = $1 AND status = false
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            basket_user = await conn.fetchrow(query, user_id)
            return basket_user
    except Exception as error:
        print(f"Ошибка в получении товаров из БД: {error}")
        
        
async def status_basket_user_expectation(user_id: int):
    query = """
    UPDATE basket
    SET status = true
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id)
    except Exception as error:
        print(f"Ошибка обновления статуса корзины пользователя {user_id} в БД: {error}")
        
        
async def get_balance_user_wheel(user_id: int):
    query = """
    SELECT stars 
    FROM wheel_balance
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            wheel_balance_user = await conn.fetchrow(query, user_id)
            return wheel_balance_user
    except Exception as error:
        print(f"Ошибка в получении количество звезд у пользователя {user_id} из БД: {error}")
        

async def get_attempt_user_wheel(user_id: int):
    query = """
    SELECT wheel_attempt 
    FROM wheel_balance
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            wheel_attempt_user = await conn.fetchrow(query, user_id)
            return wheel_attempt_user
    except Exception as error:
        print(f"Ошибка в получении количество попыток у пользователя {user_id} из БД: {error}")
        
        
async def update_wheel_user(user_id: int, stars: int, attempt: int):
    
    query = """
    UPDATE wheel_balance
    SET stars = $1, wheel_attempt = $2
    WHERE user_id = $3
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, stars, attempt, user_id)
    except Exception as error:
        print(f"Ошибка обновления в функции update_wheel_user пользователя {user_id} в БД: {error}")
            
async def update_status_notifications_wheel(user_id: int):
    query = """
    SELECT status_notifications
    FROM wheel_balance
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            status = await conn.fetchrow(query, user_id)
    except Exception as error:
        print(f"Ошибка в получении статуса колеса пользователя {user_id} из БД: {error}")
        
    if status['status_notifications']:
        return False
    
    query = """
    UPDATE wheel_balance
    SET status_notifications = true
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id)
            return True
    except Exception as error:
        print(f"Ошибка обновления в статуса попыток пользователя {user_id} в БД: {error}")
        
        
async def update_status_and_attempt_user_wheel(user_id: int):
    query = """
    UPDATE wheel_balance
    SET status_notifications = false, wheel_attempt = 3
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id)
            return True
    except Exception as error:
        print(f"Ошибка обновления возобновления статуса попыток и попыток 3 пользователя {user_id} в БД: {error}")
        
        
async def get_win_wheel_user(user_id: int):
    query = """
    SELECT stars_win_0, stars_win_2, stars_win_5, stars_win_10, stars_win_20, stars_win_50, stars_win_100, stars_win_200
    FROM wheel_user
    WHERE user_id = $1
    """
    
    try:
        pool = await Database.connect()
        async with pool.acquire() as conn:
            win_user = await conn.fetchrow(query, user_id)
            return win_user
    except Exception as error:
        print(f"Ошибка в получении win wheel пользователя {user_id} из БД: {error}")