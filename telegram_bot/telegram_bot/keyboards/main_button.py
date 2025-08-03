from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .template_button import MainMenuReply
from database.models import EquipmentCategory, Tarif, UserCategory


def get_profile_button():
    buttons = InlineKeyboardBuilder()
    buttons.row(
        InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=MainMenuReply.balance_filter)
    )
    return buttons.as_markup()

def get_category_buttons(selected_categories: list[UserCategory] | None, categories: list[EquipmentCategory]):
    if selected_categories is None:
        selected_categories = []
    user_category = [category.category_id for category in selected_categories]

    main_menu = InlineKeyboardBuilder()
    for cat in categories:
        if cat.id not in user_category and cat:
            main_menu.add(InlineKeyboardButton(text=cat.name, callback_data=f"{MainMenuReply.category_filter}{cat.id}"))
        else:
            main_menu.add(InlineKeyboardButton(text=f"✅ {cat.name}", callback_data=f"{MainMenuReply.category_filter}{cat.id}"))
    main_menu.adjust(2)
    return main_menu.as_markup()

def get_number_button(number):
    main_menu = InlineKeyboardBuilder()
    main_menu.add(InlineKeyboardButton(text=f"📞 Посмтреть номер", callback_data=f"{MainMenuReply.show_number_filter}{number}"))
    return main_menu.as_markup()

def get_tarifs_button(tarifs_list: list[Tarif]):
    main_menu = InlineKeyboardBuilder()
    for button in tarifs_list:
        if button.price == 0 or button.active == False:
            continue
        data = f"{MainMenuReply.tarif_filter}{str(button.id)}"
        main_menu.add(InlineKeyboardButton(text=f"💳{button.name} - {button.price}.00 RUB", callback_data=data))
    main_menu.adjust(1)
    return main_menu.as_markup()

def get_confirm_tarif_button(tarif_id: int):
    main_menu = InlineKeyboardBuilder()
    data = f"{MainMenuReply.tarif_confirm_filter}{str(tarif_id)}"
    main_menu.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=data),
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"{MainMenuReply.tarif_confirm_filter}cancel")
    )
    main_menu.adjust(2)
    return main_menu.as_markup()

def get_cancel_payment_button():
    main_menu = InlineKeyboardBuilder()
    main_menu.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"{MainMenuReply.cancel_payment_filter}")
    )
    main_menu.adjust(1)
    return main_menu.as_markup()

def get_confirm_payment_button():
    main_menu = InlineKeyboardBuilder()
    main_menu.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"{MainMenuReply.confirm_payment_filter}confirm"),
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"{MainMenuReply.confirm_payment_filter}cancel")
    )
    main_menu.adjust(2)
    return main_menu.as_markup()

def get_delete_tarif_buttons(tarifs: list[Tarif]):
    main_menu = InlineKeyboardBuilder() 
    for button in tarifs:
        if button.price == 0 or button.active == False:
            continue
        data = f"{MainMenuReply.delete_tarif_admin}{str(button.id)}"
        main_menu.add(InlineKeyboardButton(text=f"❌ Удалить {button.name}", callback_data=data))
    main_menu.adjust(1)
    return main_menu.as_markup()

def get_confirm_delete_tarif_button(tarif_id: int):
    main_button = InlineKeyboardBuilder()
    main_button.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"{MainMenuReply.confirm_delete_tarif_admin}{str(tarif_id)}"),
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"{MainMenuReply.confirm_delete_tarif_admin}cancel")
    )
    main_button.adjust(2)
    return main_button.as_markup()


main_menu_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [MainMenuReply.cabinet, MainMenuReply.tariffs],
        [MainMenuReply.get_orders, MainMenuReply.fqa]
    ]
)