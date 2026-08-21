from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from .config import settings
import os


# Ensure the database directory exists for absolute paths
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
if db_path and not db_path.startswith(":memory:"):
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
