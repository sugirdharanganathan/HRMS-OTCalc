from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.employee_model import Employee
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
    status: Optional[str] = Field(default="active", example="active")


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
    db_emp = Employee(emp_id=new_emp_id, **emp.model_dump())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp


@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


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
async def api_update_employee(employee_id: int, emp: EmployeeCreate, db: Session = Depends(get_db)):
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