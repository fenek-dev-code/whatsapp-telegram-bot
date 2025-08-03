from typing import Optional
from dotenv import load_dotenv
import os

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

from .config_bot import BotConfig

load_dotenv()


class Tarif(BaseModel):
    name: str
    limit_show: int
    limit_select_category: int
    price: int = 0
    tarifperiod: int | None = None

class DataBaseConfig(BaseModel):
    """ Конфигурация базы данных """
    url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")
    echo: bool = False
    max_overflow: int = 10
    pool_pre_ping: bool = True
    pool_recycle: int = 3600

    
class PaymentsConfig(BaseModel):
    """ Конфигурация платежных систем """
    AAIO_SHOP_ID: str = os.getenv("AAIO_SHOP_ID", "")
    AAIO_API_KEY: str = os.getenv("AAIO_API_KEY", "")
    AAIO_SECRET_KEY: str = os.getenv("AAIO_SECRET_KEY", "")
    PAYMENT_DESCRIPTION: str = os.getenv("PAYMENT_DESCRIPTION", "")

    MIN_DEPOSIT: int = int(os.getenv("MIN_DEPOSIT", "10"))
    MAX_DEPOSIT: int = int(os.getenv("MAX_DEPOSIT", "100000"))

class APIConfig(BaseModel):
    """ Конфигурация API """
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8080"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "secret")

class AppConfig(BaseModel):
    """ Конфигурация приложения """
    category: list[str] = [
        "Автотройдар", "Автокран", "Бетоновая", "Вульфанар", "Каток", "Композитор (ПУАТО)", 
        "Манипулятор", "Механическая", "Мини-экспозитор", "Полномоченное иммунское", 
        "Самоход", "Газер", "Трантор", "Тран", "Фронтальный погрузчик", "Шахмад (администра)", 
        "Эвакуатор", "Экспозитор гусеничный", "Экспозитор колючий", "Экспозитор погрузчик", 
        "Ямбар", "Гамблер", "Вилки грунта", "Норудика материалы", "Гайки", "Фура", 
        "Принц грунта", "Вибрация рукоятки", "Автомашин", "Наличие", "Заказы за пределами", 
        "Индекс", "Крышку", "Контриксер", "Фреза", "Бетонная", "Темперационный погрузчик", 
        "Вилки лигал", "Декларирован экспозиторы",
    ]
    tarifs: list[Tarif] = [
        Tarif(name="Путь к успеху", limit_show=30, limit_select_category=5, price=2000.0, tarifperiod=30),
    ]
    base_tarif: Tarif = Tarif(
        name=os.getenv("BASE_TARIF_NAME", "Базовый тариф"),
        limit_show=int(os.getenv("BASE_TARIF_LIMIT_SHOW", 1)), 
        limit_select_category=int(os.getenv("BASE_TARIF_LIMIT_CATEGORY", 3)),
    )

class Settings(BaseSettings):
    """Основные настройки приложения"""
    database: DataBaseConfig = DataBaseConfig()
    bot: BotConfig = BotConfig()
    payments: PaymentsConfig = PaymentsConfig()
    api: APIConfig = APIConfig()
    app: AppConfig = AppConfig()
    test: bool = os.getenv("TEST", "false").lower() == "true"
    model_config = SettingsConfigDict(env_file=".env", extra = "allow")


try:
    config = Settings()
    logger.success("Конфигурация успешно загружена")
    logger.debug(f"API порт: {config.api.port}")
except Exception as e:
    logger.critical(f"Ошибка загрузки конфигурации: {e}")
    raise SystemExit(1)