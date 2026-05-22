from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.employee_document import EmployeeDocument


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Employee(Base):
    __tablename__ = "Employees"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    curp: Mapped[str] = mapped_column(String(18), nullable=False, unique=True)
    rfc: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=text("(UTC_TIMESTAMP())"),
    )
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    documents: Mapped[list[EmployeeDocument]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )
