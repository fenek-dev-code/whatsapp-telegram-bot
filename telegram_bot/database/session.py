from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from settings.settings import config
from loguru import logger

engine = create_async_engine(
    url=config.database.url, 
    echo=config.database.echo,
    max_overflow=config.database.max_overflow,
    pool_pre_ping=config.database.pool_pre_ping,
    pool_recycle=config.database.pool_recycle
)
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        await session.close()


async def init_db():
    configure_mappers()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы успешно созданы")

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Таблицы успешно удалены")
        await engine.dispose()
        logger.info("Подключение к базе данных закрыто")


    

