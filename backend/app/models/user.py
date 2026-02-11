import enum
from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    client = "client"
    operator = "operator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    addresses = relationship("Address", back_populates="user", lazy="selectin")
    orders = relationship(
        "Order",
        back_populates="user",
        lazy="selectin",
        foreign_keys="[Order.user_id]",
    )
    roles = relationship("UserRole", back_populates="user", lazy="selectin")


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)

    user = relationship("User", back_populates="roles")
