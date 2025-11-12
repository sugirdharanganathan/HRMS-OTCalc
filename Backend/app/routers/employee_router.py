from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.employee_model import Employee, Hod, Supervisor
from app.services.excel_service import create_or_append_to_excel, write_employees_to_excel, update_employee, delete_employee
from fastapi.responses import FileResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EmployeeCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    designation: Optional[str] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    hod: Optional[str] = None
    supervisor: Optional[str] = None
    is_hod: Optional[str] = Field(default="no", description="yes or no", examples=["yes", "no"])
    is_supervisor: Optional[str] = Field(default="no", description="yes or no", examples=["yes", "no"])
    status: Optional[str] = Field(default="active", example="active")

    @field_validator("is_hod", "is_supervisor", mode="before")
    @classmethod
    def validate_yes_no(cls, value: Optional[str]) -> str:
        if value is None:
            return "no"
        if isinstance(value, bool):
            return "yes" if value else "no"
        normalized = value.strip().lower()
        if normalized not in {"yes", "no"}:
            raise ValueError("Value must be either 'yes' or 'no'")
        return normalized

    @model_validator(mode="after")
    def enforce_reporting_hierarchy(self):
        self.hod = self.hod.strip() if isinstance(self.hod, str) else self.hod
        self.hod = self.hod or None
        self.supervisor = self.supervisor.strip() if isinstance(self.supervisor, str) else self.supervisor
        self.supervisor = self.supervisor or None

        if self.is_hod == "yes":
            self.hod = None
        elif not self.hod:
            raise ValueError("hod is required when is_hod is 'no'")

        if self.is_supervisor == "yes":
            self.supervisor = None
        elif not self.supervisor:
            raise ValueError("supervisor is required when is_supervisor is 'no'")

        return self


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    hod: Optional[str] = None
    supervisor: Optional[str] = None
    is_hod: Optional[str] = Field(default=None, description="yes or no", examples=["yes", "no"])
    is_supervisor: Optional[str] = Field(default=None, description="yes or no", examples=["yes", "no"])
    status: Optional[str] = Field(default=None, example="active")

    @field_validator("is_hod", "is_supervisor", mode="before")
    @classmethod
    def validate_yes_no(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, bool):
            return "yes" if value else "no"
        normalized = value.strip().lower()
        if normalized not in {"yes", "no"}:
            raise ValueError("Value must be either 'yes' or 'no'")
        return normalized

    @model_validator(mode="after")
    def trim_reporting_fields(self):
        self.hod = self.hod.strip() if isinstance(self.hod, str) else self.hod
        self.hod = self.hod or None
        self.supervisor = self.supervisor.strip() if isinstance(self.supervisor, str) else self.supervisor
        self.supervisor = self.supervisor or None
        return self


class EmployeeOut(BaseModel):
    id: int
    emp_id: str
    name: str
    designation: Optional[str] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    hod: Optional[str] = None
    supervisor: Optional[str] = None
    status: Optional[str] = Field(default="active")

    class Config:
        # This line was changed from orm_mode = True
        from_attributes = True


@router.post("/", response_model=EmployeeOut)
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    # Get the current maximum emp_id number
    max_emp = db.query(Employee).order_by(Employee.emp_id.desc()).first()
    if max_emp and max_emp.emp_id:
        # Extract the number from EMP001 format and increment
        current_num = int(max_emp.emp_id[3:])
        next_num = current_num + 1
    else:
        # Start with 1 if no existing employees
        next_num = 1
    
    # Create new emp_id in format EMP001
    new_emp_id = f"EMP{next_num:03d}"
    
    # Create employee with generated emp_id
    # Updated .dict() to .model_dump() for Pydantic v2
    payload = emp.model_dump()
    db_emp = Employee(emp_id=new_emp_id, **payload)
    db.add(db_emp)
    db.flush()

    if db_emp.is_hod == "yes":
        db.add(Hod(
            employee_id=db_emp.id,
            emp_id=db_emp.emp_id,
            name=db_emp.name,
            designation=db_emp.designation,
            salary=db_emp.salary,
            department=db_emp.department,
            status=db_emp.status,
        ))

    if db_emp.is_supervisor == "yes":
        db.add(Supervisor(
            employee_id=db_emp.id,
            emp_id=db_emp.emp_id,
            name=db_emp.name,
            designation=db_emp.designation,
            salary=db_emp.salary,
            department=db_emp.department,
            status=db_emp.status,
        ))

    db.commit()
    db.refresh(db_emp)
    return db_emp


@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


class HodOut(BaseModel):
    id: int
    employee_id: int
    emp_id: str
    name: str
    designation: Optional[str] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class SupervisorOut(BaseModel):
    id: int
    employee_id: int
    emp_id: str
    name: str
    designation: Optional[str] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


@router.get("/hods", response_model=List[HodOut])
def list_hods(db: Session = Depends(get_db)):
    return db.query(Hod).all()


@router.get("/supervisors", response_model=List[SupervisorOut])
def list_supervisors(db: Session = Depends(get_db)):
    return db.query(Supervisor).all()


@router.get("/export-excel", response_class=FileResponse)
def export_to_excel(db: Session = Depends(get_db)):
    """Export all employees to Excel file, appending to existing data if file exists."""
    employees = db.query(Employee).all()
    excel_path = create_or_append_to_excel(employees)
    
    # Return the Excel file as a download
    headers = {
        'Content-Disposition': 'attachment; filename="employee_data.xlsx"'
    }
    return FileResponse(
        path=excel_path,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.put("/{employee_id}", response_model=EmployeeOut)
async def api_update_employee(employee_id: int, emp: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update employee fields by primary id. Only provided fields are updated.
    DB changes are committed and the Excel file is regenerated. On error the DB
    transaction is rolled back and a 500 is returned."""
    try:
        db_emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_emp:
            raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")

        # Only update fields that were actually sent by the client
        updates = emp.model_dump(exclude_unset=True)

        # Apply updates to the SQLAlchemy model if the attribute exists
        for field, value in updates.items():
            if hasattr(db_emp, field):
                setattr(db_emp, field, value)

        db_emp.hod = db_emp.hod.strip() if isinstance(db_emp.hod, str) and db_emp.hod else None
        db_emp.supervisor = db_emp.supervisor.strip() if isinstance(db_emp.supervisor, str) and db_emp.supervisor else None

        if db_emp.is_hod == "yes":
            db_emp.hod = None
        elif not db_emp.hod:
            db.rollback()
            raise HTTPException(status_code=400, detail="hod is required when is_hod is 'no'")

        if db_emp.is_supervisor == "yes":
            db_emp.supervisor = None
        elif not db_emp.supervisor:
            db.rollback()
            raise HTTPException(status_code=400, detail="supervisor is required when is_supervisor is 'no'")

        def sync_hod_record():
            if db_emp.is_hod == "yes":
                existing = db.query(Hod).filter(Hod.employee_id == db_emp.id).first()
                if existing:
                    existing.name = db_emp.name
                    existing.designation = db_emp.designation
                    existing.salary = db_emp.salary
                    existing.department = db_emp.department
                    existing.status = db_emp.status
                else:
                    db.add(Hod(
                        employee_id=db_emp.id,
                        emp_id=db_emp.emp_id,
                        name=db_emp.name,
                        designation=db_emp.designation,
                        salary=db_emp.salary,
                        department=db_emp.department,
                        status=db_emp.status,
                    ))
            else:
                db.query(Hod).filter(Hod.employee_id == db_emp.id).delete(synchronize_session=False)

        def sync_supervisor_record():
            if db_emp.is_supervisor == "yes":
                existing = db.query(Supervisor).filter(Supervisor.employee_id == db_emp.id).first()
                if existing:
                    existing.name = db_emp.name
                    existing.designation = db_emp.designation
                    existing.salary = db_emp.salary
                    existing.department = db_emp.department
                    existing.status = db_emp.status
                else:
                    db.add(Supervisor(
                        employee_id=db_emp.id,
                        emp_id=db_emp.emp_id,
                        name=db_emp.name,
                        designation=db_emp.designation,
                        salary=db_emp.salary,
                        department=db_emp.department,
                        status=db_emp.status,
                    ))
            else:
                db.query(Supervisor).filter(Supervisor.employee_id == db_emp.id).delete(synchronize_session=False)

        sync_hod_record()
        sync_supervisor_record()

        db.add(db_emp)
        db.commit()
        db.refresh(db_emp)

        # Regenerate Excel to reflect the updated DB state (best-effort)
        try:
            all_emps = db.query(Employee).all()
            write_employees_to_excel(all_emps)
        except Exception:
            # don't fail the request if excel write fails
            pass

        return db_emp
    except HTTPException:
        # re-raise HTTP 404
        raise
    except Exception as e:
        # rollback transaction on unexpected errors
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{employee_id}")
async def api_delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Delete an employee by primary id. Regenerates Excel after deletion.
    Rolls back the DB transaction on error."""
    try:
        db_emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_emp:
            raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")

        db.delete(db_emp)
        db.commit()

        # Regenerate Excel to reflect deletion (best-effort)
        try:
            all_emps = db.query(Employee).all()
            write_employees_to_excel(all_emps)
        except Exception:
            pass

        return {"detail": "Employee deleted"}
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))