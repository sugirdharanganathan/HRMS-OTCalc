from __future__ import annotations
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from decimal import Decimal
from datetime import datetime
from app.models.employee_model import Employee
from app.models.ot_base_calculation_model import OTBaseCalculation
from app.models.ot_configuration_approval_model import OtConfigurationApproval
from app.services.ot_service import upsert_ot_calculation, aggregate_monthly_hours, calculate_ot_salary


def sync_approval_row(db: Session, emp_id: str, period_month: str) -> OtConfigurationApproval:
    # Validate employee
    emp = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not emp:
        raise ValueError("Employee not found")
    if emp.salary is None or float(emp.salary) <= 0:
        raise ValueError("Invalid or missing salary")

    # Try to get or create/update OT base calculation first to have a source of truth
    obc = upsert_ot_calculation(db=db, emp_id=emp_id, period_month=period_month)

    base_salary = Decimal(str(obc.salary))
    total_work_hours = Decimal(str(obc.total_work_hours))
    ot_hours = Decimal(str(obc.ot_hours))
    ot_salary = Decimal(str(obc.ot_salary))
    net_salary = base_salary + ot_salary

    existing = (
        db.query(OtConfigurationApproval)
        .filter(OtConfigurationApproval.emp_id == emp_id, OtConfigurationApproval.period_month == period_month)
        .first()
    )
    if existing:
        # Preserve approval state columns
        existing.emp_name = emp.name
        existing.designation = emp.designation
        existing.base_salary = base_salary
        existing.total_work_hours = total_work_hours
        existing.ot_hours = ot_hours
        existing.ot_salary = ot_salary
        existing.net_salary = net_salary
        existing.ot_calc_id = int(obc.id)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    row = OtConfigurationApproval(
        emp_id=emp.emp_id,
        emp_name=emp.name,
        designation=emp.designation,
        base_salary=base_salary,
        total_work_hours=total_work_hours,
        ot_hours=ot_hours,
        ot_salary=ot_salary,
        net_salary=net_salary,
        period_month=period_month,
        ot_calc_id=int(obc.id),
        sent_for_approval=False,
        approval_pending=False,
        is_approved=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def send_for_approval(db: Session, emp_id: str) -> OtConfigurationApproval:
    row = (
        db.query(OtConfigurationApproval)
        .filter(OtConfigurationApproval.emp_id == emp_id)
        .order_by(OtConfigurationApproval.created_at.desc())
        .first()
    )
    if not row:
        raise ValueError("Approval row not found for employee")
    if row.sent_for_approval:
        return row
    row.sent_for_approval = True
    row.sent_at = datetime.utcnow()
    row.approval_pending = True
    row.is_approved = None
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_pending(db: Session, emp_id: Optional[str] = None) -> List[OtConfigurationApproval]:
    q = db.query(OtConfigurationApproval).filter(OtConfigurationApproval.approval_pending == True)
    if emp_id:
        q = q.filter(OtConfigurationApproval.emp_id == emp_id)
    # MySQL sorts NULLs last when using DESC, so no need for NULLS LAST (unsupported in MySQL)
    return q.order_by(OtConfigurationApproval.sent_at.desc()).all()


def approve_row(db: Session, emp_id: str, approved_by: Optional[str], approval_notes: Optional[str]) -> OtConfigurationApproval:
    row = (
        db.query(OtConfigurationApproval)
        .filter(OtConfigurationApproval.emp_id == emp_id, OtConfigurationApproval.approval_pending == True)
        .order_by(OtConfigurationApproval.created_at.desc())
        .first()
    )
    if not row:
        raise ValueError("Approval row not found or not pending")
    row.is_approved = True
    row.approved_at = datetime.utcnow()
    row.approved_by = approved_by
    row.approval_notes = approval_notes
    row.approval_pending = False
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def reject_row(db: Session, emp_id: str, approved_by: Optional[str], approval_notes: Optional[str]) -> OtConfigurationApproval:
    row = (
        db.query(OtConfigurationApproval)
        .filter(OtConfigurationApproval.emp_id == emp_id, OtConfigurationApproval.approval_pending == True)
        .order_by(OtConfigurationApproval.created_at.desc())
        .first()
    )
    if not row:
        raise ValueError("Approval row not found or not pending")
    row.is_approved = False
    row.approved_at = datetime.utcnow()
    row.approved_by = approved_by
    row.approval_notes = approval_notes
    row.approval_pending = False
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_by_emp(db: Session, emp_id: str, period_month: Optional[str] = None) -> List[OtConfigurationApproval]:
    q = db.query(OtConfigurationApproval).filter(OtConfigurationApproval.emp_id == emp_id)
    if period_month:
        q = q.filter(OtConfigurationApproval.period_month == period_month)
    return q.order_by(OtConfigurationApproval.created_at.desc()).all()


