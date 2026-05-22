from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmployeeDocumentCreate(BaseModel):
    employee_id: int
    document_type: str = Field(max_length=100)
    original_file_name: str = Field(max_length=255)
    storage_key: str = Field(max_length=500)
    mime_type: str = Field(max_length=100)
    size_bytes: int = Field(ge=0)


class EmployeeDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    document_type: str
    original_file_name: str
    storage_key: str
    mime_type: str
    size_bytes: int
    uploaded_at_utc: datetime
