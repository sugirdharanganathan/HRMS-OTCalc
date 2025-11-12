from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import urllib.parse
import logging
from sqlalchemy import text as _sql_text

load_dotenv()

# Provide safe defaults if env vars are missing
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "otc_hrms")

# Prefer pymysql dialect if available; fall back to mysqlconnector if you installed it
DB_DRIVER = os.getenv("DB_DRIVER", "pymysql")  # allowed: pymysql or mysqlconnector

if DB_DRIVER == "pymysql":
    dialect = "mysql+pymysql"
else:
    dialect = "mysql+mysqlconnector"

# URL-encode username/password in case they contain special chars
user = urllib.parse.quote_plus(DB_USER)
password = urllib.parse.quote_plus(DB_PASSWORD)

DATABASE_URL = f"{dialect}://{user}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# create engine with pool_pre_ping to avoid stale connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Yield a database session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create database tables (if they don't exist)."""
    Base.metadata.create_all(bind=engine)
    _ensure_employee_role_flags()
    _ensure_attendance_columns()
    _ensure_ot_table()
    _ensure_ot_configuration_approval_table()


def _ensure_employee_role_flags():
    """Add is_hod and is_supervisor columns to employees table if missing."""
    try:
        with engine.connect() as conn:
            res = conn.execute(_sql_text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'employees'
            """), {"db": os.getenv("DB_NAME", "otc_hrms")})
            existing = {row[0].lower() for row in res.fetchall()}

            alter_statements = []
            if "is_hod" not in existing:
                alter_statements.append("ADD COLUMN is_hod VARCHAR(3) NOT NULL DEFAULT 'no'")
            if "is_supervisor" not in existing:
                alter_statements.append("ADD COLUMN is_supervisor VARCHAR(3) NOT NULL DEFAULT 'no'")

            if alter_statements:
                stmt = "ALTER TABLE employees " + ", ".join(alter_statements)
                conn.execute(_sql_text(stmt))
                conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Employee role flag migration skipped or failed: {e}")


def _ensure_attendance_columns():
    """Lightweight migration: add working_hours, ot_hours, ot columns to attendance if missing."""
    try:
        with engine.connect() as conn:
            # Check existing columns
            res = conn.execute(_sql_text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'attendance'
            """), {"db": os.getenv("DB_NAME", "otc_hrms")})
            existing = {row[0].lower() for row in res.fetchall()}

            alter_statements = []
            if "working_hours" not in existing:
                alter_statements.append("ADD COLUMN working_hours FLOAT NULL")
            if "ot_hours" not in existing:
                alter_statements.append("ADD COLUMN ot_hours FLOAT NULL")
            if "ot" not in existing:
                alter_statements.append("ADD COLUMN ot TINYINT(1) NULL")

            if alter_statements:
                stmt = "ALTER TABLE attendance " + ", ".join(alter_statements)
                conn.execute(_sql_text(stmt))
                conn.commit()
    except Exception as e:
        # Log and continue; app can still run even if alter fails
        logging.getLogger(__name__).warning(f"Attendance column migration skipped or failed: {e}")


def _ensure_ot_table():
    """Create ot_base_calculation table and indexes if missing (idempotent)."""
    try:
        with engine.connect() as conn:
            # Check if table exists
            res = conn.execute(_sql_text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = :db AND table_name = 'ot_base_calculation'
            """), {"db": os.getenv("DB_NAME", "otc_hrms")})
            exists = res.scalar() > 0

            if not exists:
                conn.execute(_sql_text("""
                    CREATE TABLE ot_base_calculation (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        emp_id VARCHAR(16) NOT NULL,
                        emp_name VARCHAR(255) NOT NULL,
                        salary DECIMAL(14,2) NOT NULL,
                        period_month CHAR(7) NOT NULL,
                        total_work_hours DECIMAL(8,2) NOT NULL,
                        ot_hours DECIMAL(8,2) NOT NULL,
                        hourly_rate DECIMAL(14,6) NOT NULL,
                        ot_salary DECIMAL(14,2) NOT NULL,
                        breakdown JSON NOT NULL,
                        ot TINYINT(1) NOT NULL DEFAULT 0,
                        calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT ux_emp_period UNIQUE (emp_id, period_month),
                        INDEX idx_period_month (period_month),
                        INDEX idx_emp_id (emp_id),
                        CONSTRAINT fk_ot_emp FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                conn.commit()
            else:
                # Ensure schema conforms: drop notes if present, add ot if missing
                cols = conn.execute(_sql_text("""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'ot_base_calculation'
                """), {"db": os.getenv("DB_NAME", "otc_hrms")}).fetchall()
                existing = {r[0].lower() for r in cols}
                alters = []
                if "notes" in existing:
                    alters.append("DROP COLUMN notes")
                if "ot" not in existing:
                    alters.append("ADD COLUMN ot TINYINT(1) NOT NULL DEFAULT 0")
                if alters:
                    conn.execute(_sql_text("ALTER TABLE ot_base_calculation " + ", ".join(alters)))
                    conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(f"OT table ensure skipped or failed: {e}")


def _ensure_ot_configuration_approval_table():
    """Create ot_configuration_approval table and indexes if missing; align schema if exists."""
    try:
        with engine.connect() as conn:
            res = conn.execute(_sql_text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = :db AND table_name = 'ot_configuration_approval'
            """), {"db": os.getenv("DB_NAME", "otc_hrms")})
            exists = res.scalar() > 0

            if not exists:
                conn.execute(_sql_text("""
                    CREATE TABLE ot_configuration_approval (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        emp_id VARCHAR(16) NOT NULL,
                        emp_name VARCHAR(255) NOT NULL,
                        designation VARCHAR(255) NULL,
                        base_salary DECIMAL(14,2) NOT NULL,
                        total_work_hours DECIMAL(8,2) NOT NULL,
                        ot_hours DECIMAL(8,2) NOT NULL,
                        ot_salary DECIMAL(14,2) NOT NULL,
                        net_salary DECIMAL(14,2) NOT NULL,
                        period_month CHAR(7) NOT NULL,
                        sent_for_approval TINYINT(1) NOT NULL DEFAULT 0,
                        sent_at TIMESTAMP NULL DEFAULT NULL,
                        approval_pending TINYINT(1) NOT NULL DEFAULT 0,
                        is_approved TINYINT(1) NULL DEFAULT NULL,
                        approved_at TIMESTAMP NULL DEFAULT NULL,
                        approved_by VARCHAR(32) NULL,
                        approval_notes TEXT NULL,
                        ot_calc_id BIGINT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        CONSTRAINT fk_oca_emp FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
                        CONSTRAINT fk_oca_otcalc FOREIGN KEY (ot_calc_id) REFERENCES ot_base_calculation(id) ON DELETE SET NULL,
                        UNIQUE KEY ux_emp_period (emp_id, period_month),
                        INDEX idx_period_month (period_month),
                        INDEX idx_sent_for_approval (sent_for_approval),
                        INDEX idx_approval_pending (approval_pending),
                        INDEX idx_is_approved (is_approved)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                conn.commit()
            else:
                # Ensure important columns and keys exist (lightweight alignment)
                cols = conn.execute(_sql_text("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'ot_configuration_approval'
                """), {"db": os.getenv("DB_NAME", "otc_hrms")}).fetchall()
                existing = {r[0].lower() for r in cols}
                alters = []
                # Ensure approved_by is VARCHAR(32)
                # MySQL cannot easily check type in INFORMATION_SCHEMA reliably; attempt modify regardless
                alters.append("MODIFY COLUMN approved_by VARCHAR(32) NULL")
                if alters:
                    conn.execute(_sql_text("ALTER TABLE ot_configuration_approval " + ", ".join(alters)))
                    conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(f"OT approval table ensure skipped or failed: {e}")
