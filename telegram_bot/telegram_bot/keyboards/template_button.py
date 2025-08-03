from aiogram.types import KeyboardButton, InlineKeyboardButton

class MainMenuReply:
    get_orders = KeyboardButton(text="🚜 Получить заказы")
    tariffs = KeyboardButton(text="📝 Тарифы")
    cabinet = KeyboardButton(text="🚪 Личный кабинет")
    rent = KeyboardButton(text="🛠 Арендовать технику")
    fqa = KeyboardButton(text="📞 Поддержка")
    

    balance_filter = "balance"
    category_filter = "category:"
    tarif_filter = "tarif:"
    tarif_confirm_filter = "confirm:tarif:"
    show_number_filter = "show:number:"
    cancel_payment_filter = "cansel:payment"
    confirm_payment_filter = "confirm:payment:"

    delete_tarif_admin = "select:delete:tarif:"
    confirm_delete_tarif_admin = "delete:tarif:"