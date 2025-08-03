from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from loguru import logger

from database.requests.tarif import TarifRepository as tarif_repo
from database.session import get_session
from database.models import DatabaseError
from telegram_bot.common.state_context import CreateTarifState as state_context
from telegram_bot.common.message_generate import UserGenerateMessage as generator

from settings.settings import config
from telegram_bot.keyboards import main_button, template_button

router = Router()


@router.message(F.text == config.bot.Commands.ADMIN_CMD_CANCEL, StateFilter("*"))
async def admin_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено", reply_markup=main_button.main_menu_buttons)

@router.message(F.text == config.bot.Commands.ADMIN_CMD, StateFilter("*"))
async def admin_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=generator.generate_admin_message_menu(message.from_user.id), reply_markup=None
    )


@router.message(F.text == config.bot.Commands.ADMIN_CMD_CREATE)
async def admin_create_tarif(message: types.Message, state: FSMContext):
    if message.from_user.id in config.bot.BOT_ADMINS:
        await message.answer("Введите название тарифа, например: Премиум, Базовый, Стандарт\nИли напишите /cancel для отмены", reply_markup=None)
        await state.set_state(state_context.NAME)


@router.message(F.text, StateFilter(state_context.NAME))
async def admin_capture_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену тарифа (в рублях) \nСтрого целочисленное например: 1000", reply_markup=None)
    await state.set_state(state_context.PRICE)

@router.message(F.text, StateFilter(state_context.PRICE))
async def admin_capture_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Введите лимит показов тарифа, например: 10/100\n Строго целочисленное", reply_markup=None)
    await state.set_state(state_context.LIMIT_SHOW)

@router.message(F.text, StateFilter(state_context.LIMIT_SHOW))
async def admin_capture_limit_show(message: types.Message, state: FSMContext):
    await state.update_data(limit_show=message.text)
    await message.answer("Введите лимит категорий тарифа, например: 10/100\n Строго целочисленное", reply_markup=None)
    await state.set_state(state_context.LIMIT_CATEGORY)

@router.message(F.text, StateFilter(state_context.LIMIT_CATEGORY))
async def admin_capture_limit_category(message: types.Message, state: FSMContext):
    await state.update_data(limit_category=message.text)
    await message.answer("Введите длительность тарифа в днях, например: 7/30", reply_markup=None)
    await state.set_state(state_context.PERIOD)

@router.message(F.text, StateFilter(state_context.PERIOD))
async def admin_capture_period(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)
    data = await state.get_data()
    try:
        async with get_session() as session:
            tarif = await tarif_repo.create_tarif(**data, session=session)
            text = (
                f"Тариф: {tarif.name}"
                f"\nЦена: {tarif.price}"
                f"\nЛимит показов: {tarif.limit_show}"
                f"\nЛимит категорий: {tarif.limit_category}"
                f"\nДлительность: {tarif.period}"
                f"\nID: {tarif.id}"
                "\n\nТариф создан!"
            )
        await message.answer(text, reply_markup=None)
    except DatabaseError as e:
        await message.answer(f"{e.message}", reply_markup=None)
    await state.clear()


@router.message(F.text == config.bot.Commands.ADMIN_CMD_DELETE)
async def admin_select_tarif_delete(message: types.Message, state: FSMContext):
    if message.from_user.id in config.bot.BOT_ADMINS:
        async with get_session() as session:
            tarifs = await tarif_repo.get_tarifs(session)
            buttons = main_button.get_delete_tarif_buttons(tarifs)
            await message.answer("Выберите тариф для удаления или нажмите /cancel для отмены", reply_markup=buttons)
            await state.set_state(state_context.DELETE)


@router.callback_query(F.data.startswith(template_button.MainMenuReply.delete_tarif_admin), StateFilter(state_context.DELETE))
async def admin_delete_tarif(call: types.CallbackQuery, state: FSMContext):
    async with get_session() as session:
        try:
            tarif_id = int(call.data.split(":")[-1])
            tarif = await tarif_repo.get_tarif_by_id(tarif_id, session)
            if not tarif: 
                await call.answer("Тариф не найден", show_alert=True)
                return
            
            await state.update_data(tarif_id=tarif_id)
            button = main_button.get_confirm_delete_tarif_button(tarif_id)
            await call.message.edit_text(f"Вы действительно хотите удалить тариф: {tarif.name}?", reply_markup=button)
            await state.set_state(state_context.CONFIRM)
        except DatabaseError as e:
            await call.answer(f"{e.message}", show_alert=True)


@router.callback_query(F.data.startswith(template_button.MainMenuReply.confirm_delete_tarif_admin), StateFilter(state_context.CONFIRM))
async def admin_confirm_delete_tarif(call: types.CallbackQuery, state: FSMContext):
    if call.data.split(":")[-1] == "cancel":
        await call.message.edit_text("Удаление тарифа отменено", reply_markup=None)
        await state.clear()
        return
    async with get_session() as session:
        try:
            tarif_id = int(call.data.split(":")[-1])
            await tarif_repo.deactivate_tarif(tarif_id, session)
            await call.message.edit_text("Тариф удален", reply_markup=None)
        except DatabaseError as e:
            await call.answer(f"{e.message}", show_alert=True)
    await state.clear()