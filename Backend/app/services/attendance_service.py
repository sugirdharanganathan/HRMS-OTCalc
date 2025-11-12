from typing import Optional
from sqlalchemy.orm import Session
from app.models.attendance_model import Attendance
from app.models.employee_model import Employee
from app.services.excel_service import write_attendance_to_excel
from datetime import datetime
from datetime import timedelta


def _parse_time_or_datetime(val: Optional[str]) -> Optional[datetime]:
    """Try to parse a time or datetime string into a datetime object.
    If the input looks like a time (e.g. '9:00 AM' or '17:00'), combine it with today's date.
    Returns None if parsing fails."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    s = str(val).strip()
    # Common formats to try
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%I:%M %p",
        "%I:%M%p",
        "%H:%M",
        "%H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            # If format was time-only, combine with today
            if fmt in ("%I:%M %p", "%I:%M%p", "%H:%M", "%H:%M:%S"):
                today = datetime.now().date()
                return datetime.combine(today, dt.time())
            return dt
        except Exception:
            continue
    # Try dateutil if available for more forgiving parsing
    try:
        # Import locally to avoid a hard dependency; if dateutil isn't installed we'll skip it
        try:
            from dateutil import parser as _dateutil_parser  # type: ignore
        except Exception:
            _dateutil_parser = None

        if _dateutil_parser:
            dt = _dateutil_parser.parse(s)
            return dt
        return None
    except Exception:
        return None


def _compute_hours(clock_in: Optional[datetime], clock_out: Optional[datetime]) -> tuple[Optional[float], Optional[float], Optional[bool]]:
    """Compute working hours, OT hours, and OT flag given clock-in/out.
    Returns (working_hours, ot_hours, ot_flag)."""
    if not clock_in or not clock_out:
        return None, None, None
    try:
        delta: timedelta = clock_out - clock_in
        total_hours = max(delta.total_seconds() / 3600.0, 0.0)
        # round to 2 decimals for storage consistency
        total_hours = round(total_hours, 2)
        ot_hours = round(max(total_hours - 9.0, 0.0), 2)
        ot_flag = ot_hours > 0.0
        return total_hours, ot_hours, ot_flag
    except Exception:
        return None, None, None


def create_attendance(db: Session, data: dict) -> Attendance:
    # Parse clock_in/clock_out strings into datetimes if present
    if "clock_in" in data:
        parsed_ci = _parse_time_or_datetime(data.get("clock_in"))
        data["clock_in"] = parsed_ci
    if "clock_out" in data:
        parsed_co = _parse_time_or_datetime(data.get("clock_out"))
        data["clock_out"] = parsed_co

    # If an emp_id was provided, try to resolve the employee name and populate `name`
    emp_id_val = data.get("emp_id")
    if emp_id_val:
        emp = db.query(Employee).filter(Employee.emp_id == emp_id_val).first()
        if emp:
            data["name"] = emp.name

    # Compute derived hours if possible
    working_hours, ot_hours, ot_flag = _compute_hours(data.get("clock_in"), data.get("clock_out"))
    data["working_hours"] = working_hours
    data["ot_hours"] = ot_hours
    data["ot"] = ot_flag

    att = Attendance(**data)
    db.add(att)
    db.commit()
    db.refresh(att)

    # Regenerate full attendance excel to reflect all rows and updated columns
    try:
        all_att = db.query(Attendance).all()
        write_attendance_to_excel(all_att)
    except Exception:
        pass

    return att


def list_attendance(db: Session):
    return db.query(Attendance).all()


def get_attendance_by_emp_id(db: Session, emp_id: str) -> Optional[Attendance]:
    """Get the latest attendance record for an employee."""
    return db.query(Attendance).filter(Attendance.emp_id == emp_id).order_by(Attendance.created_at.desc()).first()


def update_attendance(db: Session, emp_id: str, data: dict) -> Optional[Attendance]:
    att = get_attendance_by_emp_id(db, emp_id)
    if not att:
        return None

    allowed = {"emp_id", "name", "clock_in", "clock_out"}
    for k, v in data.items():
        if k in allowed:
            if k in ("clock_in", "clock_out"):
                v = _parse_time_or_datetime(v)
            # If emp_id is being changed, look up the employee and update name as well
            if k == "emp_id":
                emp = db.query(Employee).filter(Employee.emp_id == v).first()
                if emp:
                    att.name = emp.name
            setattr(att, k, v)

    # Recompute derived hours after updates
    working_hours, ot_hours, ot_flag = _compute_hours(att.clock_in, att.clock_out)
    att.working_hours = working_hours
    att.ot_hours = ot_hours
    att.ot = ot_flag

    db.add(att)
    db.commit()
    db.refresh(att)

    # regenerate full attendance excel
    try:
        all_att = db.query(Attendance).all()
        write_attendance_to_excel(all_att)
    except Exception:
        pass

    return att


def delete_attendance(db: Session, emp_id: str) -> bool:
    # Delete ALL attendance rows for this employee to prevent stale rows in exports
    rows = db.query(Attendance).filter(Attendance.emp_id == emp_id).all()
    if not rows:
        return False
    for r in rows:
        db.delete(r)
    db.commit()

    try:
        all_att = db.query(Attendance).all()
        write_attendance_to_excel(all_att)
    except Exception:
        pass

    return True
