from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Строка подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"  # файл бд в sqlite, в котором вся бд

# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True)  # echo - логирование

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(
    bind=engine
)  # фабрика сеансов. Новые экз-ры сеансов при вызове

DATABASE_URL = config("DATABASE_URL")

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)
# expire_on_commit=False — сохраняет предыдущее состояние объекта без refresh.


class Base(DeclarativeBase):
    pass
