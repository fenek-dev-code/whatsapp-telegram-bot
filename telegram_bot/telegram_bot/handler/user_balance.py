from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext 
from aaio import AAIO

from database.models.payment import Payment
from settings.settings import config
from telegram_bot.keyboards import main_button, template_button
from database.requests.user import UserRepository as user_repo
from database.session import get_session
from database.models import DatabaseError
from telegram_bot.common.message_generate import UserGenerateMessage as generator
from telegram_bot.common.state_context import PaymentState
from uuid import uuid4
from database.requests.payment import PaymentRepository as payment_repo

router = Router()
client = AAIO(
    merchant_id=config.payments.AAIO_SHOP_ID,
    secret_1=config.payments.AAIO_SECRET_KEY,
    api_key=config.payments.AAIO_API_KEY
)

@router.callback_query(F.data == template_button.MainMenuReply.balance_filter)
async def callback_balance(call: types.CallbackQuery, state: FSMContext):
    async with get_session() as session:
        try:
            user = await user_repo.get_user(call.from_user.id, session)
            await state.update_data(msg_id=call.message.message_id)
            await call.message.edit_text(generator.generate_balance_message_payment(user), reply_markup=main_button.get_cancel_payment_button())
            await state.set_state(PaymentState.PAYMENT)
        except DatabaseError as e:
            await call.answer(f"{e.message}")
            await call.message.answer(f"{e.message}")
            await state.clear()

@router.message(F.text, StateFilter(PaymentState.PAYMENT))
async def mesage_payment_sum(message: types.Message, state: FSMContext):
    try:
        summa = int(message.text)
        if message.from_user.id not in config.bot.BOT_ADMINS:
            if summa <= 0 or summa > 1000000:
                raise ValueError
            if summa < config.payments.MIN_DEPOSIT:
                raise ValueError
            if summa > config.payments.MAX_DEPOSIT:
                raise ValueError

    except ValueError:
        await message.answer("Введите корректную сумму")
        return
    
    payment_url = await client.get_pay_url(
        amount=float(summa), 
        us_key=message.from_user.id, 
        order_id=payment_url,
        description=config.payments.PAYMENT_DESCRIPTION
    )
    async with get_session() as session:
        await payment_repo.create_payment(
            payment=Payment(user_id=message.from_user.id, amount=summa, payment_id=payment_url), 
            session=session
        )

    button = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Оплатить", url=payment_url, callback_data=f"status:payment:{payment_url}")]]
    )
    msg_id = (await state.get_data()).get("msg_id")
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=msg_id)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(generator.generate_payment_message(summa), reply_markup=button)
    await state.set_state(PaymentState.CONFIRM)



@router.callback_query(F.data.startswith("status:payment:"), StateFilter(PaymentState.CONFIRM))
async def callback_payment_status(call: types.CallbackQuery, state: FSMContext):
    payment_id = call.data.split(":")[-1]
    response = await client.get_payment_info(payment_id)
    button = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Проверить", callback_data=f"status:payment:{payment_id}")]]
    )
    if response.is_success():
        await call.message.edit_text("Оплата прошла успешно", reply_markup=None)
        async with get_session() as session:
            await payment_repo.update_payment_status(payment_id, response.status, session)
            await user_repo.up_balance(call.from_user.id, int(response.amount), session)
        await call.bot.send_message(
            chat_id=config.bot.ADMIN_CHANNEL, 
            text=generator.generate_payment_message_success_from_admin(
                payment_id=payment_id,
                amount=response.amount,
                status=response.status,
                payment_at=response.date,
                telegram_id=int(response.us_vars) or call.from_user.id
            )
        )
        await state.clear()
        return
    if response.is_in_process():
        await call.message.edit_text("Оплата в процессе", reply_markup=button)
        return

    await call.message.edit_text("Оплата не прошла", reply_markup=None)


