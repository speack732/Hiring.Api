"""create employee tables

Revision ID: 20260521_0001
Revises:
Create Date: 2026-05-21 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260521_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "Employees",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(length=150), nullable=False),
        sa.Column("last_name", sa.String(length=150), nullable=False),
        sa.Column("middle_name", sa.String(length=150), nullable=True),
        sa.Column("curp", sa.String(length=18), nullable=False),
        sa.Column("rfc", sa.String(length=13), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at_utc",
            sa.DateTime(timezone=True),
            server_default=sa.text("(UTC_TIMESTAMP())"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("curp", name="uq_Employees_curp"),
        sa.UniqueConstraint("rfc", name="uq_Employees_rfc"),
    )

    op.create_table(
        "EmployeeDocuments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.BigInteger(), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "uploaded_at_utc",
            sa.DateTime(timezone=True),
            server_default=sa.text("(UTC_TIMESTAMP())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["Employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_EmployeeDocuments_employee_id"),
        "EmployeeDocuments",
        ["employee_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_EmployeeDocuments_employee_id"), table_name="EmployeeDocuments")
    op.drop_table("EmployeeDocuments")
    op.drop_table("Employees")
