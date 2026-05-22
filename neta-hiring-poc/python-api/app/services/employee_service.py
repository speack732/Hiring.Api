import logging
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.models.employee import Employee
from app.models.employee_document import EmployeeDocument
from app.repositories.employee_document_repository import EmployeeDocumentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.schemas.employee_document import EmployeeDocumentCreate
from app.services.exceptions import DuplicateEmployeeError, FileValidationError
from app.storage.backblaze_storage_service import BackblazeStorageService


logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


class EmployeeService:
    def __init__(
        self,
        db: Session,
        storage_service: BackblazeStorageService | None = None,
    ) -> None:
        self.db = db
        self.storage_service = storage_service
        self.employee_repository = EmployeeRepository(db)
        self.document_repository = EmployeeDocumentRepository(db)

    def get_employee(self, employee_id: int) -> Employee | None:
        return self.employee_repository.get_by_id(employee_id)

    def list_employees(self, skip: int = 0, limit: int = 100) -> list[Employee]:
        return self.employee_repository.list(skip=skip, limit=limit)

    def create_employee(self, employee_in: EmployeeCreate) -> Employee:
        return self.employee_repository.create(employee_in)

    async def create_employee_with_documents(
        self,
        employee_in: EmployeeCreate,
        document1: UploadFile,
        document2: UploadFile,
    ) -> Employee:
        if self.storage_service is None:
            raise RuntimeError("Storage service is required for document uploads.")

        await self._validate_required_file(document1, "document1")
        await self._validate_required_file(document2, "document2")

        normalized_employee = self._normalize_employee(employee_in)
        uploaded_keys: list[str] = []

        try:
            with self.db.begin():
                if self.employee_repository.exists_by_curp_or_rfc(
                    normalized_employee.curp,
                    normalized_employee.rfc,
                ):
                    raise DuplicateEmployeeError(
                        "Ya existe un empleado con el mismo CURP o RFC."
                    )

                employee = Employee(**normalized_employee.model_dump())
                self.employee_repository.add(employee)
                self.db.flush()

                document_payloads = [
                    ("Document1", "documento-1", document1),
                    ("Document2", "documento-2", document2),
                ]

                for document_type, storage_folder, file in document_payloads:
                    storage_key = self._build_storage_key(
                        employee.id,
                        storage_folder,
                        file.filename or "document",
                    )
                    await self.storage_service.upload_async(file, storage_key)
                    uploaded_keys.append(storage_key)

                    document = EmployeeDocument(
                        employee_id=employee.id,
                        document_type=document_type,
                        original_file_name=file.filename or "document",
                        storage_key=storage_key,
                        mime_type=file.content_type or "application/octet-stream",
                        size_bytes=await self._get_file_size(file),
                    )
                    self.document_repository.add(document)

                self.db.flush()

            self.db.refresh(employee)
            logger.info(
                "employee_created",
                extra={
                    "_structured": {
                        "employee_id": employee.id,
                        "document_count": len(employee.documents),
                    }
                },
            )
            return employee
        except DuplicateEmployeeError:
            self.db.rollback()
            logger.info(
                "employee_duplicate_detected",
                extra={
                    "_structured": {
                        "curp": normalized_employee.curp,
                        "rfc": normalized_employee.rfc,
                    }
                },
            )
            raise
        except IntegrityError as exc:
            self.db.rollback()
            await self._cleanup_uploaded_files(uploaded_keys)
            logger.info(
                "employee_duplicate_constraint_detected",
                extra={
                    "_structured": {
                        "curp": normalized_employee.curp,
                        "rfc": normalized_employee.rfc,
                    }
                },
            )
            raise DuplicateEmployeeError(
                "Ya existe un empleado con el mismo CURP o RFC."
            ) from exc
        except Exception:
            self.db.rollback()
            await self._cleanup_uploaded_files(uploaded_keys)
            logger.exception(
                "employee_create_failed",
                extra={"_structured": {"uploaded_keys": uploaded_keys}},
            )
            raise

    def update_employee(
        self,
        employee_id: int,
        employee_in: EmployeeUpdate,
    ) -> Employee | None:
        employee = self.employee_repository.get_by_id(employee_id)
        if employee is None:
            return None

        return self.employee_repository.update(employee, employee_in)

    def delete_employee(self, employee_id: int) -> bool:
        employee = self.employee_repository.get_by_id(employee_id)
        if employee is None:
            return False

        self.employee_repository.delete(employee)
        return True

    def add_document(
        self,
        document_in: EmployeeDocumentCreate,
    ) -> EmployeeDocument:
        return self.document_repository.create(document_in)

    def list_documents(self, employee_id: int) -> list[EmployeeDocument]:
        return self.document_repository.list_by_employee_id(employee_id)

    async def _validate_required_file(self, file: UploadFile, field_name: str) -> None:
        size = await self._get_file_size(file)
        if size <= 0:
            raise FileValidationError(f"El archivo {field_name} es requerido.")

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise FileValidationError(
                f"Tipo de archivo no permitido: {file.content_type}"
            )

        if size > MAX_FILE_SIZE_BYTES:
            raise FileValidationError(
                "El archivo excede el tamano maximo permitido de 10 MB."
            )

        await file.seek(0)

    async def _get_file_size(self, file: UploadFile) -> int:
        def get_size() -> int:
            current_position = file.file.tell()
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(current_position)
            return size

        return await run_in_threadpool(get_size)

    def _normalize_employee(self, employee_in: EmployeeCreate) -> EmployeeCreate:
        return EmployeeCreate(
            first_name=employee_in.first_name.strip(),
            last_name=employee_in.last_name.strip(),
            middle_name=employee_in.middle_name.strip()
            if employee_in.middle_name
            else None,
            curp=employee_in.curp.strip().upper(),
            rfc=employee_in.rfc.strip().upper(),
            email=str(employee_in.email).strip(),
            phone_number=employee_in.phone_number.strip(),
            address=employee_in.address.strip() if employee_in.address else None,
            birth_date=employee_in.birth_date,
            created_by=employee_in.created_by,
        )

    def _build_storage_key(
        self,
        employee_id: int,
        document_type: str,
        original_file_name: str,
    ) -> str:
        extension = Path(original_file_name).suffix
        safe_file_name = f"{uuid4().hex}{extension}"
        return f"employees/{employee_id}/{document_type}/{safe_file_name}"

    async def _cleanup_uploaded_files(self, uploaded_keys: list[str]) -> None:
        if self.storage_service is None:
            return

        for key in uploaded_keys:
            try:
                await self.storage_service.delete_async(key)
            except Exception:
                logger.warning(
                    "uploaded_file_cleanup_failed",
                    extra={"_structured": {"storage_key": key}},
                    exc_info=True,
                )
