from database.session import get_session
from database.models import Tarif, EquipmentCategory
from loguru import logger
from settings.settings import config
from sqlalchemy import select


class IinitializeDataBase:

    @staticmethod
    async def initialize_categories():
        async with get_session() as session:
            logger.info("Инициализация категорий...")
            result = await session.execute(select(EquipmentCategory.name))
            existing_categories = {name for (name,) in result.all()}
            new_categories = [
                EquipmentCategory(name=name) 
                for name in config.app.category
                if name not in existing_categories
            ]
            if new_categories:
                session.add_all(new_categories)
                await session.commit()
                logger.info("Категории успешно созданы")
            else:
                logger.info("Категории уже существуют")
            await session.close()
    @staticmethod
    async def initialize_tarifs():
        async with get_session() as session:
            logger.info("Инициализация тарифов...")
            result = await session.execute(select(Tarif.name))
            existing_tarifs = {name for (name,) in result.all()}
            new_tarifs = [
                Tarif(
                    name=tarif.name,
                    limit_show=tarif.limit_show,
                    limit_category=tarif.limit_select_category,
                    price=tarif.price, 
                    period=tarif.tarifperiod
                ) 
                for tarif in config.app.tarifs
                if tarif.name not in existing_tarifs
            ]
            if new_tarifs:
                session.add_all(new_tarifs)
                await session.commit()
                logger.info("Тарифы успешно созданы")
            else:
                logger.info("Тарифы уже существуют")
            await session.close()
