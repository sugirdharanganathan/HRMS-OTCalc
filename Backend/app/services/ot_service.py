from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal, ROUND_HALF_UP
from app.models.employee_model import Employee
from app.models.attendance_model import Attendance
from app.models.ot_base_calculation_model import OTBaseCalculation


def _round_money(value: float | Decimal, places: int = 2) -> float:
    q = Decimal(value).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
    return float(q)


def calculate_ot_salary(salary: float, total_work_hours: float) -> Dict[str, Any]:
    HOURS_BASE = 173.0
    ot_hours = max(0.0, round(total_work_hours - HOURS_BASE, 2))
    hourly_rate = salary / HOURS_BASE
    remaining = ot_hours
    bands = []

    # 1st hour @1.5
    h1 = min(1.0, remaining)
    amt1 = _round_money(h1 * 1.5 * hourly_rate, 2)
    bands.append({"name": "1st_hour", "hours": h1, "multiplier": 1.5, "amount": amt1})
    remaining -= h1

    # 2nd..7th @2.0 (up to 6 hours)
    h2 = min(6.0, max(0.0, remaining))
    amt2 = _round_money(h2 * 2.0 * hourly_rate, 2)
    bands.append({"name": "2nd_to_7th", "hours": h2, "multiplier": 2.0, "amount": amt2})
    remaining -= h2

    # 8th @3.0
    h3 = min(1.0, max(0.0, remaining))
    amt3 = _round_money(h3 * 3.0 * hourly_rate, 2)
    bands.append({"name": "8th_hour", "hours": h3, "multiplier": 3.0, "amount": amt3})
    remaining -= h3

    # 9th+ @4.0
    h4 = max(0.0, remaining)
    amt4 = _round_money(h4 * 4.0 * hourly_rate, 2)
    bands.append({"name": "9th_and_beyond", "hours": h4, "multiplier": 4.0, "amount": amt4})

    total_ot_salary = _round_money(sum(b["amount"] for b in bands), 2)
    breakdown = {
        "salary": _round_money(salary, 2),
        "hourly_rate": round(hourly_rate, 6),
        "total_work_hours": round(total_work_hours, 2),
        "ot_hours": round(ot_hours, 2),
        "bands": bands,
        "total_ot_salary": total_ot_salary,
    }
    return {
        "ot_hours": ot_hours,
        "hourly_rate": round(hourly_rate, 6),
        "ot_salary": total_ot_salary,
        "breakdown": breakdown,
    }


def aggregate_monthly_hours(db: Session, emp_id: str, period_month: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Sum working_hours and ot_hours for the given month from attendance.
    Returns (total_work_hours, total_ot_hours). period_month formatted as 'YYYY-MM'.
    """
    try:
        year = int(period_month.split("-")[0])
        month = int(period_month.split("-")[1])
    except Exception:
        return None, None

    total_work_hours = (
        db.query(func.sum(Attendance.working_hours))
        .filter(
            Attendance.emp_id == emp_id,
            extract("year", Attendance.clock_in) == year,
            extract("month", Attendance.clock_in) == month,
            Attendance.clock_in.isnot(None),
            Attendance.clock_out.isnot(None),
        )
        .scalar()
    )
    total_ot_hours = (
        db.query(func.sum(Attendance.ot_hours))
        .filter(
            Attendance.emp_id == emp_id,
            extract("year", Attendance.clock_in) == year,
            extract("month", Attendance.clock_in) == month,
            Attendance.clock_in.isnot(None),
            Attendance.clock_out.isnot(None),
        )
        .scalar()
    )
    if total_work_hours is None and total_ot_hours is None:
        return None, None
    work = None if total_work_hours is None else float(round(total_work_hours, 2))
    ot = None if total_ot_hours is None else float(round(total_ot_hours, 2))
    return work, ot


def upsert_ot_calculation(
    db: Session,
    emp_id: str,
    period_month: str
) -> OTBaseCalculation:
    emp: Optional[Employee] = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not emp:
        raise ValueError("Employee not found")
    if emp.salary is None or float(emp.salary) <= 0:
        raise ValueError("Invalid or missing salary")

    # Always derive totals from attendance
    total_work_hours, total_ot_hours_month = aggregate_monthly_hours(db, emp_id=emp_id, period_month=period_month)
    if total_work_hours is None:
        raise ValueError("Total work hours could not be derived for the specified period")

    calc = calculate_ot_salary(float(emp.salary), float(total_work_hours))
    ot_flag = bool(total_ot_hours_month and total_ot_hours_month > 0)

    # If no OT in the month, set amounts to zero and ot_hours=0 regardless of base overage
    if not ot_flag:
        calc["ot_hours"] = 0.0
        calc["ot_salary"] = 0.0
        calc["breakdown"]["ot_hours"] = 0.0
        calc["breakdown"]["total_ot_salary"] = 0.0
        # Zero out band hours/amounts
        for band in calc["breakdown"]["bands"]:
            band["hours"] = 0
            band["amount"] = 0.0

    existing: Optional[OTBaseCalculation] = (
        db.query(OTBaseCalculation)
        .filter(OTBaseCalculation.emp_id == emp_id, OTBaseCalculation.period_month == period_month)
        .first()
    )

    if existing:
        existing.emp_name = emp.name
        existing.salary = Decimal(str(emp.salary))
        existing.total_work_hours = Decimal(str(round(float(total_work_hours), 2)))
        existing.ot_hours = Decimal(str(round(calc["ot_hours"], 2)))
        existing.hourly_rate = Decimal(str(round(calc["hourly_rate"], 6)))
        existing.ot_salary = Decimal(str(round(calc["ot_salary"], 2)))
        existing.breakdown = calc["breakdown"]
        existing.ot = ot_flag
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    record = OTBaseCalculation(
        emp_id=emp.emp_id,
        emp_name=emp.name,
        salary=Decimal(str(emp.salary)),
        period_month=period_month,
        total_work_hours=Decimal(str(round(float(total_work_hours), 2))),
        ot_hours=Decimal(str(round(calc["ot_hours"], 2))),
        hourly_rate=Decimal(str(round(calc["hourly_rate"], 6))),
        ot_salary=Decimal(str(round(calc["ot_salary"], 2))),
        breakdown=calc["breakdown"],
        ot=ot_flag,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


