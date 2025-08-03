from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from aiogram.types.user import User as UserTG

from database.models import User,  DatabaseError, Tarif
from settings.settings import config
from loguru import logger


class UserRepository:

    async def create_user(user: UserTG, session: AsyncSession):
        tarif = config.app.base_tarif
        db_tarif = Tarif(
            name=tarif.name, 
            limit_show=tarif.limit_show, 
            limit_category=tarif.limit_select_category, 
            price=tarif.price, 
            period=tarif.tarifperiod
        )
        session.add(db_tarif)
        await session.flush()
        balance = 0
        if user.id in config.bot.BOT_ADMINS:
            balance += config.bot.ADMIN_BALANCE

        user = User(
            telegram_id=user.id, 
            username=user.username,
            full_name=user.full_name,
            balance=balance,
            current_tarif=db_tarif
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"Пользователь ID - {user.telegram_id} зарегистрирован")
        return user

    async def get_user(telegram_id: int, session: AsyncSession) -> User:
        try:
            user = await session.scalar(
                select(User).where(User.telegram_id == telegram_id)
                .options(
                    selectinload(User.selected_categories),
                    selectinload(User.current_tarif)
                )
            )
            return user
        except Exception as e:
            logger.error(e)
            return DatabaseError(message="Пользователь не найден, нажмите /start")

        
    async def show_number_user(telegram_id: int, session: AsyncSession) -> None:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id).options(
                selectinload(User.current_tarif)
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise DatabaseError(message="Пользователь не найден, нажмите /start")
        if user.current_tarif is None:
            raise DatabaseError(message="Вы не выбрали тариф")
        if not user.can_show():
            raise DatabaseError(message="Вы исчерпали лимит просмотров")
        if not user.check_tarif_period():
            raise DatabaseError(message="Срок действия тарифа истёк")
        user.daily_show_used += 1
        await session.commit()
        await session.close()

    async def up_balance(telegram_id: int, balance: int, session: AsyncSession) -> None:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        user.balance += balance
        await session.commit()
        await session.close()



        


