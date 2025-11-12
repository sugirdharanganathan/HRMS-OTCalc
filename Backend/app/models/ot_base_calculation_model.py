from sqlalchemy import Column, Integer, String, DECIMAL, JSON, TIMESTAMP, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class OTBaseCalculation(Base):
    __tablename__ = "ot_base_calculation"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # NOTE: In this codebase, foreign keys reference employees.emp_id (STRING),
    # so we align with existing design to avoid breaking changes.
    emp_id = Column(String(16), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=False, index=True)
    emp_name = Column(String(255), nullable=False)
    salary = Column(DECIMAL(14, 2), nullable=False)
    period_month = Column(String(7), nullable=False, index=True)  # "YYYY-MM"
    total_work_hours = Column(DECIMAL(8, 2), nullable=False)
    ot_hours = Column(DECIMAL(8, 2), nullable=False)
    hourly_rate = Column(DECIMAL(14, 6), nullable=False)
    ot_salary = Column(DECIMAL(14, 2), nullable=False)
    breakdown = Column(JSON, nullable=False)
    ot = Column(Boolean, nullable=False, default=False)
    calculated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    __table_args__ = (
        UniqueConstraint('emp_id', 'period_month', name='ux_emp_period'),
    )


