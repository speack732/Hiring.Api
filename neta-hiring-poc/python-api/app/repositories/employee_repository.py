from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, employee_id: int) -> Employee | None:
        stmt = (
            select(Employee)
            .options(selectinload(Employee.documents))
            .where(Employee.id == employee_id)
        )
        return self.db.scalar(stmt)

    def exists_by_curp_or_rfc(self, curp: str, rfc: str) -> bool:
        stmt = select(Employee.id).where((Employee.curp == curp) | (Employee.rfc == rfc))
        return self.db.scalar(stmt) is not None

    def list(self, skip: int = 0, limit: int = 100) -> list[Employee]:
        stmt = (
            select(Employee)
            .options(selectinload(Employee.documents))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, employee_in: EmployeeCreate) -> Employee:
        employee = Employee(**employee_in.model_dump())
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def add(self, employee: Employee) -> Employee:
        self.db.add(employee)
        return employee

    def update(self, employee: Employee, employee_in: EmployeeUpdate) -> Employee:
        update_data = employee_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)

        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.commit()
