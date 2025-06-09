from aiogram.types import Message

async def telegram_name_users(message: Message) -> dict:
    
    dict_name = {
        'id_user': int(message.from_user.id),
        'uname': '@' + str(message.chat.username),
        'fname': str(message.chat.first_name),
        'lname': str(message.chat.last_name),
    }
    
    return dict_name