# Стандартная библиотека
from contextlib import asynccontextmanager

# Сторонние зависимости
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

# Локальные модули
from telegram_bot.bot import app_bot
from api.webhook import app as router
from settings.settings import config
from database.requests.initialize import IinitializeDataBase as init_data
from database.session import drop_db, init_db



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    try:
        await init_db()
        await init_data.initialize_categories()
        await init_data.initialize_tarifs()
        await app_bot.start()
        logger.info("Приложение запущено [OK]")
        yield
    finally:
        await app_bot.stop()
        if config.test:
            await drop_db()
        logger.info("Приложение остановлено [OK]")


app = FastAPI(
    title="WhatsApp-Bot Integration",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host=config.api.host,
            port=config.api.port,
            log_level=config.api.log_level
        )
    except KeyboardInterrupt:
        logger.info("Сервер остановлен по запросу пользователя")
    except Exception as e:
        logger.critical(f"Критическая ошибка сервера: {e}")
        raise