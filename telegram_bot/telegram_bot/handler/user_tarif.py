from aiogram import Router, types, F
from loguru import logger

from telegram_bot.keyboards import main_button, template_button
from database.models import DatabaseError
from database.requests.tarif import TarifRepository as tarif_repo
from database.session import get_session
from telegram_bot.common.message_generate import UserGenerateMessage as generator
from settings.settings import config

router = Router()


@router.message(F.text == template_button.MainMenuReply.tariffs.text)
async def show_tarifs(
    message: types.Message, 
):
    async with get_session() as session:
        tarifs = await tarif_repo.get_tarifs(session)
        buttons = main_button.get_tarifs_button(tarifs)
        text = generator.generate_tarifs_message(tarifs)
        await message.answer(text, reply_markup=buttons)


@router.callback_query(F.data.startswith(template_button.MainMenuReply.tarif_filter))
async def call_select_tarif(
    call: types.CallbackQuery
):
    async with get_session() as session:
        tarif_id = int(call.data.split(":")[-1])
        tarif = await tarif_repo.get_tarif_by_id(tarif_id, session)
        if not tarif:
            await call.answer("Тариф не найден", show_alert=True)
            return
        text = generator.generate_select_tarif_message(tarif)
        await call.message.edit_text(text, reply_markup=main_button.get_confirm_tarif_button(tarif_id))


@router.callback_query(F.data.startswith(template_button.MainMenuReply.tarif_confirm_filter))
async def call_confirm(
    call: types.CallbackQuery,
):
    async with get_session() as session:
        if call.data.split(':')[2] == "cancel":
            await call.message.edit_text("Вы отменили покупку тарифа", reply_markup=None)
            return
        try:
            tarif_id = int(call.data.split(':')[-1])
            user = await tarif_repo.buy_tarif_user(call.from_user.id, tarif_id, session)
            text = generator.generate_message_user_profile(user)
            admin_text = generator.generate_logg_buy_tarif(user)

            await call.message.edit_text(text, reply_markup=None)
            await call.bot.send_message(chat_id=config.bot.ADMIN_CHANNEL, text=admin_text)
        except DatabaseError as e:
            await call.answer(f"{e.message}", show_alert=True)
        except Exception as e:
            logger.error(e)
            await call.answer("Произошла ошибка, попробуйте позже", show_alert=True)
            await call.bot.send_message(
                chat_id=config.bot.ADMIN_CHANNEL, 
                text=(
                    f"Произошла ошибка при покупке тарифа\n"
                    f"Пользователь: {call.from_user.id}\n"
                    f"Тариф: {tarif_id}\n"
                    f"Ошибка: {e}"
                )
            )