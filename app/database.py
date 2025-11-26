from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

# Строка подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"  # файл бд в sqlite, в котором вся бд

# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True) # echo - логирование

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(bind=engine) # фабрика сеансов. Новые экз-ры сеансов при вызове




from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = config("DATABASE_URL")

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)






class Base(DeclarativeBase):
    pass