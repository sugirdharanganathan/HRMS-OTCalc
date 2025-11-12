from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.ot_configuration_approval_model import OtConfigurationApproval
from app.services.ot_approval_service import (
    sync_approval_row,
    send_for_approval,
    list_pending,
    approve_row,
    reject_row,
    get_by_emp,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SyncRequest(BaseModel):
    emp_id: str = Field(..., example="EMP001")
    period_month: str = Field(..., example="2025-11")


class ApproveRejectPayload(BaseModel):
    approved_by: Optional[str] = Field(None, example="EMP002")
    approval_notes: Optional[str] = Field(None, example="OK to pay")


class ApprovalRowOut(BaseModel):
    emp_id: str
    emp_name: str
    designation: Optional[str] = None
    base_salary: float
    ot_hours: float
    ot_salary: float
    net_salary: float

    class Config:
        from_attributes = True


@router.post("/sync", response_model=ApprovalRowOut)
def api_sync(payload: SyncRequest, db: Session = Depends(get_db)):
    try:
        return sync_approval_row(db, emp_id=payload.emp_id, period_month=payload.period_month)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{emp_id}/send", response_model=ApprovalRowOut)
def api_send(emp_id: str, db: Session = Depends(get_db)):
    try:
        return send_for_approval(db, emp_id=emp_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/pending", response_model=List[ApprovalRowOut])
def api_pending(emp_id: Optional[str] = None, db: Session = Depends(get_db)):
    return list_pending(db, emp_id=emp_id)


@router.put("/{emp_id}/approve", response_model=ApprovalRowOut)
def api_approve(emp_id: str, payload: ApproveRejectPayload, db: Session = Depends(get_db)):
    try:
        return approve_row(db, emp_id=emp_id, approved_by=payload.approved_by, approval_notes=payload.approval_notes)
    except ValueError as ve:
        raise HTTPException(status_code=409, detail=str(ve))


@router.put("/{emp_id}/reject", response_model=ApprovalRowOut)
def api_reject(emp_id: str, payload: ApproveRejectPayload, db: Session = Depends(get_db)):
    try:
        return reject_row(db, emp_id=emp_id, approved_by=payload.approved_by, approval_notes=payload.approval_notes)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/emp/{emp_id}", response_model=List[ApprovalRowOut])
def api_get_emp(emp_id: str, period_month: Optional[str] = None, db: Session = Depends(get_db)):
    return get_by_emp(db, emp_id=emp_id, period_month=period_month)


