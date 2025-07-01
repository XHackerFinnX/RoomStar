from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db.models.pay import get_basket_all_bot_message, update_status_checking_pay

router = Router()

@router.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split("_")[1])
    data_basket = await get_basket_all_bot_message(user_id)
    secret_id = data_basket['secret_id']
    basket_id = data_basket['basket_id']
    # Новый markup с результатом
    new_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтверждено", callback_data="noop")]
    ])

    await callback.message.edit_reply_markup(reply_markup=new_markup)

    await bot.send_message(
        chat_id=user_id,
        text=(
            "✅ <b>Ваша оплата подтверждена!</b>\n"
            "⭐ Звезды поступят на ваш аккаунт в течение <b>5 минут</b>.\n"
            "Спасибо за использование RoomStar ✨"
        ),
        parse_mode="HTML"
    )

    await callback.answer("Оплата подтверждена ✅", show_alert=False)
    
    await update_status_checking_pay(user_id, basket_id, secret_id, 'Успешно', True)


@router.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split("_")[1])
    data_basket = await get_basket_all_bot_message(user_id)
    secret_id = data_basket['secret_id']
    basket_id = data_basket['basket_id']
    # Новый markup с результатом
    new_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отклонено", callback_data="noop")]
    ])

    await callback.message.edit_reply_markup(reply_markup=new_markup)

    await bot.send_message(
        chat_id=user_id,
        text=(
            "❌ <b>Оплата отклонена</b>\n"
            "Произошла ошибка при проверке платежа.\n"
            "Пожалуйста, <b>свяжитесь с поддержкой</b> в чате, чтобы решить проблему."
        ),
        parse_mode="HTML"
    )

    await callback.answer("Оплата отклонена ❌", show_alert=False)
    
    await update_status_checking_pay(user_id, basket_id, secret_id, 'Ошибка', True)


@router.callback_query(F.data == "noop")
async def ignore_noop(callback: CallbackQuery):
    await callback.answer("⛔ Это действие уже выполнено.", show_alert=True)