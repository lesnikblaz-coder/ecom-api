import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from contextlib import contextmanager

load_dotenv(Path(__file__).resolve().parent / ".env")

class Base(DeclarativeBase):
    pass

DATABASE_URL = (f"postgresql+psycopg2://"
                f"{os.getenv("DB_USER")}:"
                f"{os.getenv("DB_PASSWORD")}@"
                f"{os.getenv("DB_HOST")}:"
                f"{os.getenv("DB_PORT")}/"
                f"{os.getenv("DB_NAME")}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def transaction(db: Session):
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise