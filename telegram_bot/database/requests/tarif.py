
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession


from database.models import Tarif, User, UserTarifHistory, DatabaseError
from datetime import datetime, timezone, timedelta
from loguru import logger

class TarifRepository:

    @staticmethod
    async def get_tarifs(session: AsyncSession):
        result = await session.scalars(select(Tarif))
        return result.all()

    @staticmethod
    async def get_tarif_by_id(id: int, session: AsyncSession) -> Tarif:
        result = await session.execute(select(Tarif).where(Tarif.id == id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def buy_tarif_user(
        telegram_id: int, 
        tarif_id: int, 
        session: AsyncSession
    ) -> User:
        """Покупка и активация тарифа пользователем"""
        try:
            user = await _get_user_with_tarif(telegram_id, session)
            tarif = await _validate_tarif(tarif_id, session)
            if user.balance < tarif.price:
                raise DatabaseError("Недостаточно средств на счету")
            
            # 2. Проверяем текущий тариф пользователя
            await _check_active_tarif(user, tarif)
            
            # 3. Рассчитываем новый период действия
            new_period = _calculate_new_period(user, tarif)
            
            # 4. Обновляем данные пользователя
            await _update_user_data(user, tarif, new_period, session)
            
            # 5. Создаем запись в истории
            await _create_tarif_history(user, tarif, session)
            
            return user
            
        except DatabaseError:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка покупки тарифа: {e}")
            raise DatabaseError("Внутренняя ошибка сервера")
        
    @staticmethod
    async def create_tarif(name: str, price: int, period: int, limit_show:int,  limit_category:int, session: AsyncSession) -> Tarif:
        tarif = Tarif(name=name, price=price, period=period, limit_show=limit_show, limit_category=limit_category)
        session.add(tarif)
        await session.commit()
        return tarif
    

    async def deactivate_tarif(tarif_id: int, session: AsyncSession) -> None:
        tarif = await _validate_tarif(tarif_id, session)
        tarif.active = False
        await session.commit()

# Вспомогательные функции
async def _get_user_with_tarif(telegram_id: int, session: AsyncSession) -> User:
    """Получаем пользователя с информацией о текущем тарифе"""
    return await session.scalar(
        select(User)
        .where(User.telegram_id == telegram_id)
        .options(joinedload(User.current_tarif))
    )

async def _validate_tarif(tarif_id: int, session: AsyncSession) -> Tarif:
    """Проверяем существование тарифа"""
    tarif = await session.get(Tarif, tarif_id)
    if not tarif:
        raise DatabaseError("Тариф не найден")
    return tarif

async def _check_active_tarif(user: User, tarif: Tarif) -> None:
    """Проверяем активный тариф пользователя"""
    current_time = datetime.now(timezone.utc)
    if user.tarif_period and user.tarif_period.replace(tzinfo=timezone.utc) < current_time:
        user.tarif_period = None
    
    if user.current_tarif_id and user.current_tarif_id != tarif.id and user.tarif_period:
        raise DatabaseError(
            f"У вас уже есть активный тариф\n"
            f"Действует до: {user.tarif_period.strftime('%d.%m.%Y')}\n"
            "Пожалуйста, дождитесь окончания текущего тарифа"
        )

def _calculate_new_period(user: User, tarif: Tarif) -> datetime:
    """Рассчитываем новый период действия тарифа"""
    # Получаем текущее время с часовым поясом
    current_time = datetime.now(timezone.utc)
    days = tarif.period
    
    if user.tarif_period is None:
        return current_time + timedelta(days=days)
    
    if user.tarif_period.tzinfo is None:
        user.tarif_period = user.tarif_period.replace(tzinfo=timezone.utc)
    
    if (user.tarif_period > current_time and 
        user.current_tarif_id == tarif.id):
        return user.tarif_period + timedelta(days=days)
    
    return current_time + timedelta(days=days)

async def _update_user_data(
    user: User, 
    tarif: Tarif, 
    new_period: datetime, 
    session: AsyncSession
) -> None:
    """Обновляем данные пользователя"""
    user.buy_tarif_at = datetime.now(timezone.utc)
    user.tarif_period = new_period
    user.daily_show_used = 0
    user.current_tarif = tarif
    user.balance -= tarif.price
    await session.commit()

async def _create_tarif_history(
    user: User, 
    tarif: Tarif, 
    session: AsyncSession
) -> None:
    """Создаем запись в истории тарифов"""
    history = UserTarifHistory(
        user_id=user.id,
        tarif_id=tarif.id,
        activated_at=datetime.now(timezone.utc)
    )
    session.add(history)
    await session.commit()
    await session.refresh(user)
        