from aiogram import types, Router, F
from aiogram.filters import CommandStart

from telegram_bot.keyboards import main_button, template_button
from database.requests.user import UserRepository as user_repo
from database.requests.category import CategoryRepository as category_repo
from database.session import get_session, AsyncSession
from database.models import DatabaseError, User
from telegram_bot.common.message_generate import UserGenerateMessage as generator

router = Router()

@router.message(CommandStart())
async def echo(message: types.Message):
    async with get_session() as session:
        user = await user_repo.get_user(message.from_user.id, session)
        if not user:
            user = await user_repo.create_user(message.from_user, session)
        text = generator.generate_start_message(user)
        await message.answer(
            text, 
            reply_markup=main_button.main_menu_buttons
        )

@router.message(F.text == template_button.MainMenuReply.cabinet.text)
async def show_cabinet(
    message: types.Message, 
):
    async with get_session() as session:
        user = await user_repo.get_user(message.from_user.id, session)
        text = generator.generate_message_user_profile(user)
        await message.answer(
            text=text, 
            reply_markup=main_button.get_profile_button()
        )


@router.message(F.text == template_button.MainMenuReply.get_orders.text)
async def get_orders(
    message: types.Message,
):
    async with get_session() as session:
        categories = await category_repo.get_categories(session)
        user: User | None = await user_repo.get_user(message.from_user.id, session)
        if not user:
            await message.answer("Вы не зарегистрированы, используйте /start")
        buttons = main_button.get_category_buttons(user.selected_categories, categories)
        text = "🚜 Выбери тип спецтехники, по которой хотите получать заказы."
        await message.answer(text, reply_markup=buttons)


@router.callback_query(F.data.startswith(template_button.MainMenuReply.category_filter))
async def callback_category(
    call: types.CallbackQuery
):
    """ Обратока выбора категории спецтехники"""
    async with get_session() as session:
        category = call.data.split(":")[1]
        category_list = await category_repo.get_categories(session)
        try:
            user = await category_repo.select_catogory(call.from_user.id, int(category), session)
            button = main_button.get_category_buttons(user.selected_categories, category_list)
            await call.answer(f"Вы выбрали категорию")
            await call.message.edit_reply_markup(reply_markup=button)
        except DatabaseError as e:
            await call.answer(f"{e.message}")
            await call.message.answer(f"{e.message}")

@router.callback_query(F.data.startswith(template_button.MainMenuReply.show_number_filter))
async def callback_show_number(
    call: types.CallbackQuery
):
    async with get_session() as session:
        try:
            await user_repo.show_number_user(call.from_user.id, session)
            number = call.data.split(":")[-1]
            await call.answer(f"Номер: {number}")
            old_message = call.message.text
            await call.message.edit_text(f"{old_message}\n\n📞 Номер: {number}") 
            button = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Перейти на WhatsApp", url=f"https://wa.me/{number}")]])
            await call.message.edit_reply_markup(reply_markup=button)
        except DatabaseError as e:
            await call.answer(f"{e.message}")
            await call.message.answer(f"{e.message}")