from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from ..extension import db


class Department(db.Model):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
