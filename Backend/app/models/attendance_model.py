from sqlalchemy import Column, Integer, String, DateTime, text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emp_id = Column(String(16), ForeignKey("employees.emp_id"), nullable=False)
    # store name redundantly for quick access in exports; will be auto-filled from Employee
    name = Column(String(255), nullable=False)
    # store clock_in/out as DateTime when possible; API can send ISO strings or time strings
    clock_in = Column(DateTime, nullable=True)
    clock_out = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    # updated_at auto-updates on row modification at the DB server side
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), nullable=True)

    # relationship to Employee for convenience (read-only usage)
    employee = relationship("Employee", primaryjoin="Attendance.emp_id==foreign(Employee.emp_id)", viewonly=True)
