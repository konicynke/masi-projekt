from datetime import datetime, date
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Date, Text, Integer, ForeignKey, func
from sqlalchemy import Enum as SQLAlchemyEnum
from ..extension import db


class LeaveRequestStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[LeaveRequestStatus] = mapped_column(SQLAlchemyEnum(LeaveRequestStatus), nullable=False, default=LeaveRequestStatus.PENDING)
    request_reason: Mapped[str | None] = mapped_column(Text)
    manager_comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id"))