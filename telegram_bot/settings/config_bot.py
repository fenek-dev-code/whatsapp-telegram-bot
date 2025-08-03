from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class BotConfig(BaseModel):
    """Конфигурация Telegram бота"""
    TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_CHANNEL: str = os.getenv("BOT_ADMIN_CHANNEL_ID", "")
    BOT_ADMINS: list[int] = [int(i) for i in os.getenv("BOT_ADMINS", "").split(",")]
    ADMIN_BALANCE: int = int(os.getenv("ADMIN_BALANCE", "2000"))
    FQA_LINK: str = os.getenv("BOT_FQA_LINK", "https://t.me/regDelar_bot")

    class Commands:
        ADMIN_CMD: str = "/admin"
        ADMIN_CMD_CREATE: str = "/create_tarif"
        ADMIN_CMD_DELETE: str = "/delete_tarif"
        ADMIN_CMD_CANCEL: str = "/cancel"

    def validate_config(self):
        if not self.TOKEN:
            raise ValueError("Токен бота не указан")
        if not self.ADMIN_CHANNEL.startswith('-100'):
            raise ValueError("ID канала должен начинаться с '-100'")
        if not self.BOT_ADMINS:
            raise ValueError("Администраторы бота не указаны")
        if not self.ADMIN_BALANCE:
            raise ValueError("Начальный баланс администратора не указан")
        if not self.FQA_LINK:
            raise ValueError("Ссылка на FQA не указана")