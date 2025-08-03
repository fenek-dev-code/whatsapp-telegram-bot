from database.models import User, EquipmentCategory, UserCategory, DatabaseError
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger   



class CategoryRepository:

    @staticmethod
    async def get_categories(session: AsyncSession) -> list[EquipmentCategory]:
        result = await session.execute(select(EquipmentCategory))
        return result.scalars().all()

    @staticmethod
    async def select_catogory(
        telegram_id: int, category_id: int, session: AsyncSession
    ) -> User | None:
        category = await session.get(EquipmentCategory, category_id)
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
            .options(
                selectinload(User.selected_categories),
                selectinload(User.current_tarif)
            )
        )
        user = result.scalar_one_or_none()
        if user.selected_categories:
            for i in range(len(user.selected_categories)):
                if user.selected_categories[i].category_id == category_id:
                    user.selected_categories[i].is_active = True
                    user.selected_categories.pop(i)
                    user.daily_select_used -= 1
                    await session.commit()
                    logger.info(f"Пользователь {telegram_id} отменил категорию {category.name}")
                    return user
    
        if not user.can_select():
            raise DatabaseError(message="Вы исчерпали лимит выбора категорий")
        
        user.selected_categories.append(UserCategory(
            user_id=user.id, 
            category_id=category_id, 
            telegram_id=telegram_id,
            category_name=category.name
        ))
        user.daily_select_used += 1
        logger.info(f"Пользователь {telegram_id} выбрал категорию {category.name}")
        await session.commit()
        return user

    @staticmethod
    async def get_users_by_category(category_name: str, session: AsyncSession) -> list[UserCategory]:
        result = await session.execute(
            select(UserCategory).where(UserCategory.category_name == category_name)
        )
        await session.close()
        return result.scalars().all()
    

