from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.services.employee_service import EmployeeService
from app.services.exceptions import DuplicateEmployeeError, FileValidationError
from app.storage.backblaze_storage_service import (
    BackblazeStorageService,
    get_storage_service,
)


router = APIRouter(prefix="/employees", tags=["employees"])


async def validate_exact_document_fields(request: Request) -> None:
    form = await request.form()
    file_fields = [
        field_name
        for field_name, value in form.multi_items()
        if isinstance(value, StarletteUploadFile)
    ]

    if len(file_fields) != 2 or set(file_fields) != {"document1", "document2"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requieren exactamente los archivos document1 y document2.",
        )


def get_employee_read_service(
    db: Session = Depends(get_db),
) -> EmployeeService:
    return EmployeeService(db=db)


def get_employee_write_service(
    db: Session = Depends(get_db),
    storage_service: BackblazeStorageService = Depends(get_storage_service),
) -> EmployeeService:
    return EmployeeService(db=db, storage_service=storage_service)


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_exact_document_fields)],
)
async def create_employee(
    first_name: Annotated[str, Form(max_length=150)],
    last_name: Annotated[str, Form(max_length=150)],
    curp: Annotated[str, Form(max_length=18)],
    rfc: Annotated[str, Form(max_length=13)],
    email: Annotated[EmailStr, Form(max_length=150)],
    phone_number: Annotated[str, Form(max_length=20)],
    birth_date: Annotated[date, Form()],
    document1: Annotated[UploadFile, File()],
    document2: Annotated[UploadFile, File()],
    middle_name: Annotated[str | None, Form(max_length=150)] = None,
    address: Annotated[str | None, Form(max_length=500)] = None,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_write_service),
) -> EmployeeRead:
    employee_in = EmployeeCreate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        curp=curp,
        rfc=rfc,
        email=email,
        phone_number=phone_number,
        address=address,
        birth_date=birth_date,
        created_by=current_user.email,
    )

    try:
        employee = await employee_service.create_employee_with_documents(
            employee_in=employee_in,
            document1=document1,
            document2=document2,
        )
    except FileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DuplicateEmployeeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return EmployeeRead.model_validate(employee)


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee_by_id(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_read_service),
) -> EmployeeRead:
    employee = employee_service.get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    return EmployeeRead.model_validate(employee)
