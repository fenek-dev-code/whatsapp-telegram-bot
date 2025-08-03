from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from settings.settings import config
import asyncio
from .handler.main_router import router
from loguru import logger

class BotApp:
    def __init__(self):
        self.bot = Bot(
            token=config.bot.TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        self.dp = Dispatcher(storage=MemoryStorage())
        self.dp.include_router(router)
        self.polling_task = None

    async def start(self):
        """Запуск бота"""
        
        self.polling_task = asyncio.create_task(self.dp.start_polling(self.bot))
        logger.info("Бот запущен [OK]")

    async def stop(self):
        """Остановка бота"""
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
            logger.info("Бот остановлен [OK]")

    async def send_message_to_user(self, chat_id: int, message: str, button=None) -> None:
        """Отправка сообщения пользователю"""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=button
            )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
try:
    app_bot = BotApp()
except TokenValidationError as err:
    logger.error(f"Ошибка валидации токена: {err}")
    raise