from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from ..extension import db
from enum import Enum


class UserRole(Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    HR = "HR"
    ADMIN = "ADMIN"


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)

    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    subordinates: Mapped[list["User"]] = relationship("User", backref="manager", remote_side=[id])