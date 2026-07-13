import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from contextlib import asynccontextmanager

from app.logging_config import logger

load_dotenv(Path(__file__).resolve().parent / ".env")

class Base(DeclarativeBase):
    pass

DATABASE_URL = (f"postgresql+asyncpg://"
                f"{os.getenv("DB_USER")}:"
                f"{os.getenv("DB_PASSWORD")}@"
                f"{os.getenv("DB_HOST")}:"
                f"{os.getenv("DB_PORT")}/"
                f"{os.getenv("DB_NAME")}")

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def transaction(db: AsyncSession):
    try:
        yield db
        await db.commit()
    except Exception:
        logger.exception("Database transaction failed")
        await db.rollback()
        raise