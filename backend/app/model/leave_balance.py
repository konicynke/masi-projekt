from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from ..extension import db

class LeaveBalance(db.Model):
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    used_days: Mapped[int] = mapped_column(Integer, default=0)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id"), nullable=False)