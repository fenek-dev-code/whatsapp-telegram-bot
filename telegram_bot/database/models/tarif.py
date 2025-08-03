
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import  ForeignKey, String, Integer
from typing import List, Optional, TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User

class Tarif(BaseModel):
    __tablename__ = "tarifs"
    
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    limit_show: Mapped[int] = mapped_column(default=1)
    limit_category: Mapped[int] = mapped_column(default=1)
    price: Mapped[int] = mapped_column(default=0)
    period: Mapped[int] = mapped_column(Integer(), default=7)
    active: Mapped[bool] = mapped_column(default=True)

    # Пользователи с этим тарифом (отношение один-ко-многим)
    current_users: Mapped[List["User"]] = relationship(
        "User", 
        back_populates="current_tarif",
        foreign_keys="[User.current_tarif_id]"
    )
    
    # История назначений этого тарифа
    tarif_history: Mapped[List["UserTarifHistory"]] = relationship(
        back_populates="tarif"
    )


class UserTarifHistory(BaseModel):
    __tablename__ = "user_tarif_history"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tarif_id: Mapped[int] = mapped_column(ForeignKey("tarifs.id"))
    activated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expired_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="tarif_history")
    tarif: Mapped["Tarif"] = relationship(back_populates="tarif_history")
