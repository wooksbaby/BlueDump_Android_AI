from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from bdconfig import DATABASE_URL, ASYNC_DATABASE_URL  # Assuming you have an async URL
from typing import Generator, AsyncGenerator


# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)
async_engine = create_async_engine(ASYNC_DATABASE_URL)  # 비동기 엔진

# 동기 및 비동기 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,  # 비동기 엔진을 사용
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db  # 세션을 반환하고
    finally:
        db.close()  # 요청이 끝나면 세션을 닫음


# 비동기 데이터베이스 세션을 생성하는 함수
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session  # 세션을 반환하고
        finally:
            await session.close()  # 요청이 끝나면 세션을 닫음
