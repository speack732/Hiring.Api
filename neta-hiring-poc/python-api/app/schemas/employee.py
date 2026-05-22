from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.employee_document import EmployeeDocumentRead


class EmployeeBase(BaseModel):
    first_name: str = Field(max_length=150)
    last_name: str = Field(max_length=150)
    middle_name: str | None = Field(default=None, max_length=150)
    curp: str = Field(max_length=18)
    rfc: str = Field(max_length=13)
    email: EmailStr = Field(max_length=150)
    phone_number: str = Field(max_length=20)
    address: str | None = Field(default=None, max_length=500)
    birth_date: date
    created_by: str | None = Field(default=None, max_length=100)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)
    middle_name: str | None = Field(default=None, max_length=150)
    curp: str | None = Field(default=None, max_length=18)
    rfc: str | None = Field(default=None, max_length=13)
    email: EmailStr | None = Field(default=None, max_length=150)
    phone_number: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    birth_date: date | None = None
    created_by: str | None = Field(default=None, max_length=100)


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at_utc: datetime
    documents: list[EmployeeDocumentRead] = Field(default_factory=list)
