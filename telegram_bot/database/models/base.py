from database.session import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

class BaseModel(Base):
    """Базовая модель с общими полями"""
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

class DatabaseError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)