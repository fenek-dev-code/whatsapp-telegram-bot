from datetime import datetime
import re
from fastapi import APIRouter, Request, HTTPException, status
from loguru import logger
from typing import Any, Dict

from database.requests.category import CategoryRepository as category_repo
from database.requests.user import UserRepository as user_repo
from telegram_bot.common.message_generate import UserGenerateMessage as generator
from database.session import AsyncSession, get_session
from telegram_bot.bot import app_bot
from settings import config
from telegram_bot.keyboards import main_button
from pydantic import BaseModel
from database.models import User, DatabaseError

class WebhookData(BaseModel):
    text: str
    number: str
    category: str

app = APIRouter()

  
@app.post("/webhook/whatsapp/{token}")
async def whatsapp_webhook(
    request: Request,
    token: str
) -> Dict[str, str]:
    """Обработчик входящих вебхуков от WhatsApp"""
    if token != config.api.webhook_secret: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный токен авторизации"
        )

    try:
        # Получаем JSON данные напрямую из запроса
        data = await request.json()
        
        # Валидируем данные
        if not all(key in data for key in ["text", "number", "category"]):
            raise ValueError("Отсутствуют обязательные поля")
            
        async with get_session() as session:
            await process_webhook_message(
                data["text"], 
                data["number"], 
                data["category"], 
                session
            )
        return {"status": "success"}

    except ValueError as e:
        logger.warning(f"Некорректные данные: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

def remove_phone_numbers(text):
    phone_pattern = r'(?:\+7|7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
    
    return re.sub(phone_pattern, '', text)

async def process_webhook_message(
    text: str,
    number: str,
    category: str,
    session: AsyncSession
) -> None:
    """Обработка входящего сообщения"""
    category_users = await category_repo.get_users_by_category(category, session)
    if not category_users or len(category_users) == 0:
        logger.info(f"Нет пользователей для категории: {category}")
        return

    message = generator.generate_show_whatapp_message(text, category)
    button = main_button.get_number_button(number)
    message = remove_phone_numbers(message)
    for user_category in category_users:
        try:
            current_user: User | None = await user_repo.get_user(user_category.telegram_id, session)
            if current_user is None:
                logger.error(f"Пользователь не найден: {user_category.telegram_id}")
                continue
            if current_user.last_limit_update.date() < datetime.utcnow().date():
                current_user.reset_daily_limits()
                logger.info(f"Лимиты пользователя {current_user.telegram_id} обновлены")
                
        except DatabaseError as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            continue
        await app_bot.send_message_to_user(user_category.telegram_id, message, button)
        logger.info(f"Сообщение c категории {category} отправлено пользователю с id: {user_category.telegram_id}")

    logger.info(f"Сообщение c категории {category} отправлено {len(category_users)} пользователям")
    await session.commit()
    await session.close()

