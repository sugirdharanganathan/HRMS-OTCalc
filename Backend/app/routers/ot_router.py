from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.ot_base_calculation_model import OTBaseCalculation
from app.services.ot_service import upsert_ot_calculation

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class OTCalculateRequest(BaseModel):
    emp_id: str = Field(..., example="EMP001")
    period_month: str = Field(..., example="2025-11")  # YYYY-MM


class OTCalculationResponse(BaseModel):
    id: int
    emp_id: str
    emp_name: str
    salary: float
    period_month: str
    total_work_hours: float
    ot_hours: float
    hourly_rate: float
    ot_salary: float
    breakdown: Dict[str, Any]
    calculated_at: Optional[Any] = None
    ot: bool

    class Config:
        from_attributes = True


@router.post("/calculate", response_model=OTCalculationResponse)
def calculate_and_store(payload: OTCalculateRequest, db: Session = Depends(get_db)):
    try:
        rec = upsert_ot_calculation(
            db=db,
            emp_id=payload.emp_id,
            period_month=payload.period_month
        )
        return rec
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/{emp_id}", response_model=List[OTCalculationResponse])
def list_ot_for_employee(emp_id: str, period: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(OTBaseCalculation).filter(OTBaseCalculation.emp_id == emp_id)
    if period:
        q = q.filter(OTBaseCalculation.period_month == period)
    return q.order_by(OTBaseCalculation.calculated_at.desc()).all()

