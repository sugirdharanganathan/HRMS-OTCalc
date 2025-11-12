from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, CHAR, Text, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.sql import func
from app.database import Base


class OtConfigurationApproval(Base):
    __tablename__ = "ot_configuration_approval"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # In this codebase, canonical reference is employees.emp_id (string)
    emp_id = Column(String(16), ForeignKey("employees.emp_id", ondelete="CASCADE"), nullable=False, index=True)

    emp_name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=True)

    base_salary = Column(DECIMAL(14, 2), nullable=False)
    total_work_hours = Column(DECIMAL(8, 2), nullable=False)
    ot_hours = Column(DECIMAL(8, 2), nullable=False)
    ot_salary = Column(DECIMAL(14, 2), nullable=False)
    net_salary = Column(DECIMAL(14, 2), nullable=False)

    period_month = Column(CHAR(7), nullable=False, index=True)  # YYYY-MM

    sent_for_approval = Column(Boolean, default=False, nullable=False, index=True)
    sent_at = Column(TIMESTAMP, nullable=True)
    approval_pending = Column(Boolean, default=False, nullable=False, index=True)
    is_approved = Column(Boolean, nullable=True, index=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    approved_by = Column(String(32), nullable=True)
    approval_notes = Column(Text, nullable=True)

    ot_calc_id = Column(Integer, ForeignKey("ot_base_calculation.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


