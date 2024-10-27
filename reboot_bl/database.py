from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from bdconfig import DATABASE_URL
from typing import Generator

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# DB 주소 (Google Cloud SQL을 위한 MySQL 연결 문자열)


# 데이터베이스 세션을 생성하는 함수
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db  # 세션을 반환하고
    finally:
        db.close()  # 요청이 끝나면 세션을 닫음