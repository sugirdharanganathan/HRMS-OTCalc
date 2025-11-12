from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    # primary auto-increment id
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emp_id = Column(String(16), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=True)
    salary = Column(Float, nullable=True)
    department = Column(String(255), nullable=True)
    hod = Column(String(255), nullable=True)
    supervisor = Column(String(255), nullable=True)
    is_hod = Column(String(3), nullable=False, server_default=text("'no'"))
    is_supervisor = Column(String(3), nullable=False, server_default=text("'no'"))
    status = Column(String(16), server_default=text("'active'"), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), nullable=True)


class Hod(Base):
    __tablename__ = "hods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True)
    emp_id = Column(String(16), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=True)
    salary = Column(Float, nullable=True)
    department = Column(String(255), nullable=True)
    status = Column(String(16), server_default=text("'active'"), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), nullable=True)


class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True)
    emp_id = Column(String(16), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=True)
    salary = Column(Float, nullable=True)
    department = Column(String(255), nullable=True)
    status = Column(String(16), server_default=text("'active'"), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), nullable=True)
