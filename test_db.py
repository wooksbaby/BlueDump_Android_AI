import os
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

# 데이터베이스 URL 설정
DATABASE_URL = f"mysql+asyncmy://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_IP')}/{os.getenv('DB_NAME')}"

# SQLAlchemy 엔진 및 세션 설정
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

app = FastAPI() 

async def get_db():
    async with async_session() as session:
        yield session

@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    # 데이터베이스 관련 로직
    return {"message": "DB 연결 성공"}

