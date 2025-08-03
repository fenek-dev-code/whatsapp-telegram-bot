from typing import List, TYPE_CHECKING
from .base import BaseModel
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, UniqueConstraint

if TYPE_CHECKING:
    from .user import User



class UserCategory(BaseModel):
    __tablename__ = "user_categories"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    telegram_id: Mapped[int] = mapped_column(index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("equipment_categories.id"), index=True)
    category_name: Mapped[str|None] = mapped_column(String(128), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship(back_populates="selected_categories")
    category: Mapped["EquipmentCategory"] = relationship(back_populates="selected_by_users")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'category_id', name='uq_user_category'),
    )

class EquipmentCategory(BaseModel):
    __tablename__ = "equipment_categories"
    
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=False)

    selected_by_users: Mapped[List["UserCategory"]] = relationship(
        back_populates="category",
        lazy="raise"
    )