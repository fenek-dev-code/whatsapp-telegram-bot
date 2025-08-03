from datetime import datetime
from settings import config
from database.models import User, Tarif



class UserGenerateMessage:
    @staticmethod
    def generate_message_user_profile(user: User):
        show_timit_text = f"{user.daily_show_used}"
        tarif_name_text = "Пацанский тариф"
        tarif_period_text = "Лимитный тариф"
        category = f"{user.daily_select_used}/3"

        username = ""
        user_full_name = ""
        if user.username != None:
            username = f"Username: @{user.username}\n"
        if user.full_name != None:
            user_full_name = f"Full name: {user.full_name}\n"
        if user.current_tarif != None:
            show_timit_text = f"{user.daily_show_used}/{user.current_tarif.limit_show}"
            tarif_name_text = f"{user.current_tarif.name}"
            category = f"{user.daily_select_used}/{user.current_tarif.limit_category}"
            if user.tarif_period != None:
                tarif_period_text = f"{user.tarif_period.strftime('%d.%m %Y %H:%M')}"

        return (
            f"👤 <b>USER PROFILE</b> <i>\nID - {user.telegram_id}\n{username}{user_full_name}</i>\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 <b>Ваш баланс:</b> {user.balance} RUB\n"
            f"💳 <b>Ваш текущий тариф:</b> {tarif_name_text}\n"
            f"📅 <b>Дата окончания текущего тарифа:</b> {tarif_period_text}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👀 <b>Просмотры:</b> {show_timit_text}\n"
            f"📚 <b>Категории:</b> {category}\n"
            f"━━━━━━━━━━━━━━\n"
        )
    
    @staticmethod
    def generate_start_message(user: User):
        name = ""
        try:
            if user.username != None:
                name = f"{user.full_name}, "
        except AttributeError:
            pass

        text = (
            f"🌟 <b>{name}Добро пожаловать!</b> 🌟\n"
            "🚜 Я твой персональный <b>чат-бот для заказов спецтехники</b>!\n\n"
            "Вот что я могу для тебя сделать:\n"
            "✅ <i>Присылать свежие заявки</i> в режиме реального времени\n"
            "✅ <i>Фильтровать</i> по нужным категориям техники\n"
            "✅ <i>Уведомлять</i> о срочных заказах\n"
            "✨ <b>Как начать?</b> Просто выбери нужную категорию в меню ниже ⬇️\n\n"
            "📌 <i>Будем рады помочь с поиском клиентов!</i>\n"
        )
        if user.telegram_id in config.bot.BOT_ADMINS:
            text += f"\n👤 Администратор: {user.telegram_id} {config.bot.Commands.ADMIN_CMD}\n"
        return text
    
    @staticmethod
    def generate_admin_message_menu(user_id: int):
        if user_id in config.bot.BOT_ADMINS:
            return (
                f"👤 Администратор - {user_id}\n"
                f"📌 <b>Панель администратора</b>\n"
                f"📝 <i>Удалить Тариф</i> - {config.bot.Commands.ADMIN_CMD_DELETE}\n"
                f"📝 <i>Создать Тариф</i> - {config.bot.Commands.ADMIN_CMD_CREATE}\n"
                f"📝 <i>Отменить/Назад</i> - {config.bot.Commands.ADMIN_CMD_CANCEL}\n"
            )
    
    @staticmethod
    def generate_tarifs_message(tarifs: list[Tarif]):
        text = "📝 Выбери тариф, по которому хотите получать заказы.\n\n"
        for tarif in tarifs:
            if tarif.price == 0 or tarif.active == False:
                continue
            text += f"🤖 Тариф - {tarif.name}\n"
            text += f"━━━━━━━━━━━━━━━━━━\n"
            text += f"📞 Показов номера: {tarif.limit_show} / Сутки\n"
            text += f"📚 Количество категорий: {tarif.limit_category}\n"
            text += f"💸 Цена - {tarif.price} RUB / {tarif.period} дней.\n\n"
        return text
    
    @staticmethod
    def generate_select_tarif_message(tarif: Tarif):
        return (
            f"🤖 Вы выбрали тариф: {tarif.name}\n"
            f"📞 Показов номера: {tarif.limit_show} / Сутки\n"
            f"📚 Количество категорий: {tarif.limit_category}\n"
            f"💸 Цена - {tarif.price} RUB / {tarif.period} дней.\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 Подтвердите покупку"
        )
    
    @staticmethod
    def generate_logg_buy_tarif(user: User):
        username = ""
        if user.username != None:
            username = f"Profile link: https://t.me/@{user.username}\n"
        return (
            f"👤 Пользователь - {user.telegram_id}\n"
            f"💸 Купил тариф: {user.current_tarif.name}\n"
            f"💸 Цена - {user.current_tarif.price} RUB / {user.current_tarif.period} дней.\n"
            f"💰 Баланс - {user.balance} RUB\n"
            f"📅 Дата окончания - {user.tarif_period.strftime('%d.%m %Y')}\n"
            f"📅 Дата покупки - {user.buy_tarif_at.strftime('%d.%m %Y')}\n"
            f"{username}"
        )
    
    @staticmethod
    def generate_show_whatapp_message(message: str, category: str):
        return (
            f"<b>📞 Посмотреть номер</b>"
            f"\n\n{message}"
            f"\n\nКатегория: {category}"
        )

    @staticmethod
    def generate_balance_message_payment(user: User):
        return (
            f"👤 Пользователь - {user.telegram_id}\n"
            f"💰 Баланс - {user.balance} RUB\n\n"
            f"💸 Что бы пополнить баланс"
            f"Введите сумму на которую хотите пополнить баланс...\n"
            f"Необходимо ввести сумму в RUB без пробелов и символов\n"
            f"Больше {config.payments.MIN_DEPOSIT} RUB и меньше {config.payments.MAX_DEPOSIT} RUB.\n"            
        )
    @staticmethod
    def generate_payment_message(amount: int):
        return (
            f"💸 Сумма - {amount} RUB\n"
            "Оплата займет не более 5 минут, после оплаты вам придет уведомление\n"
            "Для оплаты нажмите на ссылку ниже 👇\n"
        )
    @staticmethod
    def generate_payment_message_success_from_admin(payment_id, amount, status, payment_at, telegram_id):
        return (
                f"💳 Новый платеж #{payment_id}\n"
                f"👤 Пользователь: {telegram_id}\n"
                f"💰 Сумма: {amount} RUB\n"
                f"🔄 Статус: {status}\n"
                f"📅 Дата платежа: {payment_at}"
        )