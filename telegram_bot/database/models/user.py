
from .base import BaseModel, DatabaseError
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from .tarif import Tarif, UserTarifHistory
    from .category import UserCategory

class User(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64))
    full_name: Mapped[Optional[str]] = mapped_column(String(128))

    balance: Mapped[int] = mapped_column(Integer(), default=0)
    daily_show_used: Mapped[int] = mapped_column(default=0)
    daily_select_used: Mapped[int] = mapped_column(default=0)
    last_limit_update: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    buy_tarif_at: Mapped[datetime | None] = mapped_column(default=None)
    tarif_period: Mapped[datetime | None] = mapped_column(default=None)
    

    current_tarif_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tarifs.id"))
    current_tarif: Mapped[Optional["Tarif"]] = relationship(
        "Tarif", 
        back_populates="current_users",
        lazy="selectin"
    )

    # История тарифов
    tarif_history: Mapped[List["UserTarifHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Выбранные категории (убрано дублирование)
    selected_categories: Mapped[List["UserCategory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def check_limits(self) -> bool:
        """Проверяет, нужно ли обновлять лимиты"""
        return datetime.utcnow().date() > self.last_limit_update.date()

    def check_tarif_period(self) -> bool:
        """Проверяет срок действия тарифа"""
        if self.tarif_period is None:
            return True
        
        current_time = datetime.now(timezone.utc)
        tarif_time = self.tarif_period.replace(tzinfo=timezone.utc) if self.tarif_period.tzinfo is None else self.tarif_period
        
        if tarif_time < current_time:
            return False
        return True

    def reset_daily_limits(self):
        """Сбрасывает дневные лимиты"""
        self.daily_show_used = 0
        self.last_limit_update = datetime.utcnow()

    def can_show(self) -> bool:
        """Проверяет доступность показа"""
        if self.check_limits():
            self.reset_daily_limits()
        return self.daily_show_used < self.current_tarif.limit_show

    def can_select(self) -> bool:
        """Проверяет доступность выбора"""
        if self.selected_categories is None:
            self.selected_categories = []
        if self.check_limits():
            self.reset_daily_limits()
        return self.daily_select_used < self.current_tarif.limit_category

    def __repr__(self) -> str:
        return f"User(telegram_id={self.telegram_id}, username={self.username})"