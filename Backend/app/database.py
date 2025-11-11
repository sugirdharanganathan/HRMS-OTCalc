from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import urllib.parse
import logging

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
