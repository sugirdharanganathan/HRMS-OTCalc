from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.database import SessionLocal
from app.models.attendance_model import Attendance
from app.services.attendance_service import create_attendance, list_attendance, update_attendance, delete_attendance
from app.services.excel_service import create_or_append_attendance_excel, write_attendance_to_excel, build_attendance_workbook_bytes
from fastapi.responses import FileResponse, StreamingResponse
from datetime import datetime

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AttendanceCreate(BaseModel):
    emp_id: str = Field(..., example="EMP001")
    name: str = Field(..., example="John Doe")
    clock_in: Optional[str] = Field(None, example="09:00 AM")  # Can be time string or ISO datetime
    clock_out: Optional[str] = Field(None, example="05:00 PM")


class AttendanceOut(BaseModel):
    id: int
    emp_id: str
    name: str
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    working_hours: Optional[float] = None
    ot_hours: Optional[float] = None
    ot: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/")
def api_create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    """Create attendance record. Accepts time strings and returns ISO-formatted datetime strings."""
    data = payload.model_dump()
    # Create record (service handles time string parsing)
    att = create_attendance(db, data)
    
    # Convert to JSON-safe format with ISO-8601 datetimes
    result = jsonable_encoder(att, custom_encoder={
        datetime: lambda dt: dt.isoformat() if dt else None
    })
    return JSONResponse(content=result)


@router.get("/")
def api_list_attendance(db: Session = Depends(get_db)):
    """List all attendance records with ISO-formatted datetime strings."""
    records = list_attendance(db)
    result = jsonable_encoder(records, custom_encoder={
        datetime: lambda dt: dt.isoformat() if dt else None
    })
    return JSONResponse(content=result)


@router.get("/export-excel")
def export_attendance(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    # Stream an in-memory workbook to avoid file locking issues and ensure latest headers/values
    xlsx_bytes = build_attendance_workbook_bytes(records)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    headers = {"Content-Disposition": f'attachment; filename="attendance_export_{ts}.xlsx"'}
    return StreamingResponse(iter([xlsx_bytes]), headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.put("/{emp_id}")
async def api_update_attendance(emp_id: str, payload: AttendanceCreate, db: Session = Depends(get_db)):
    """Update attendance record with ISO-formatted datetime strings."""
    try:
        updates = payload.model_dump(exclude_unset=True)
        updated = update_attendance(db, emp_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail=f"No attendance found for employee {emp_id}")
        
        result = jsonable_encoder(updated, custom_encoder={
            datetime: lambda dt: dt.isoformat() if dt else None
        })
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{emp_id}")
async def api_delete_attendance(emp_id: str, db: Session = Depends(get_db)):
    try:
        ok = delete_attendance(db, emp_id)
        if not ok:
            raise HTTPException(status_code=404, detail=f"No attendance found for employee {emp_id}")
        return {"detail": "Attendance deleted"}
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
