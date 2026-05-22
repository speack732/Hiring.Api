from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee_document import EmployeeDocument
from app.schemas.employee_document import EmployeeDocumentCreate


class EmployeeDocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_id: int) -> EmployeeDocument | None:
        return self.db.get(EmployeeDocument, document_id)

    def list_by_employee_id(self, employee_id: int) -> list[EmployeeDocument]:
        stmt = select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)
        return list(self.db.scalars(stmt).all())

    def create(self, document_in: EmployeeDocumentCreate) -> EmployeeDocument:
        document = EmployeeDocument(**document_in.model_dump())
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def add(self, document: EmployeeDocument) -> EmployeeDocument:
        self.db.add(document)
        return document

    def delete(self, document: EmployeeDocument) -> None:
        self.db.delete(document)
        self.db.commit()
