from .user_tarif import router as tarif_router
from .user import router as user_router
from .user_balance import router as balance_router
from .admin import router as admin_router
from aiogram import Router, types, F
from telegram_bot.keyboards import  template_button
from settings.settings import config


router = Router()
router.include_routers(tarif_router, user_router, balance_router, admin_router)




@router.message(F.text == template_button.MainMenuReply.fqa.text)
async def show_fqa(message: types.Message):
    button = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="FAQ", url=config.bot.FQA_LINK)]]
    )
    await message.answer("FAQ - часто задаваемые вопросы", reply_markup=button)



















