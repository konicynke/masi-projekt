from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, ForeignKey, Integer, String
from ..extension import db

class LeaveType(db.Model):
    __tablename__ = "leave_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(default=True)