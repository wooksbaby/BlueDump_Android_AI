from fastapi import (
    FastAPI,
    BackgroundTasks,
    File,
    UploadFile,
    HTTPException,
    Depends,
    Form,
    Body,
)
import os
import shutil
from pydantic import BaseModel
from typing import List
from gcs_controller import upload_to_gcs, download_from_gcs, handle_background_tasks
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer
from sqlalchemy.future import select

app = FastAPI()

# .env 파일 로드
dotenv_path = "/home/BlueDump/.env"
load_dotenv(dotenv_path)


# GCS 환경 변수 로드
bucket_name = os.getenv("GCS_BUCKET_NAME")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcs_folder_prefix = "rooms/"  # 기본 폴더 접두사


# DB 주소
DATABASE_URL = f"mysql+asyncmy://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_IP')}/{os.getenv('DB_NAME')}"

# SQLAlchemy 엔진 및 세션 설정
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# 회원가입 응답 모델
class SignUpResponse(BaseModel):
    message: str
    user_id: str


# 이미지 업로드 요청 모델
class UploadRequest(BaseModel):
    GROUPROOM_NUM: int
    MEMBER_NUM: int


class Message(BaseModel):
    groupID: str  # groupID를 문자열로 받음


@app.post("/signup", response_model=SignUpResponse)
async def signup(
    nickname: str = Form(...),
    id: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),  # 비밀번호 확인 필드 추가
    profile_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),  # DB 세션 주입
):
    try:
        # 비밀번호와 비밀번호 확인이 일치하는지 확인
        if password != confirm_password:
            raise HTTPException(
                status_code=400, detail="비밀번호와 비밀번호 확인이 일치하지 않습니다."
            )

        # 비밀번호 해싱 (예: bcrypt 사용)
        hashed_password = hash_password(password)  # 해시 함수 정의 필요

        # 사용자 정보 데이터베이스에 저장
        new_user = User(nickname=nickname, user_id=id, password=hashed_password)
        db.add(new_user)
        await db.commit()

        # 프로필 이미지 처리
        if profile_image:
            gcs_folder_path = f"profile_images/{id}/"  # GCS에 저장할 경로
            await upload_to_gcs(
                profile_image.file, profile_image.filename, gcs_folder_path
            )

        return SignUpResponse(message="회원 가입이 완료되었습니다.", user_id=id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회원 가입 중 오류 발생: {str(e)}")


@app.post("/upload/")
async def upload_files(
    upload_request: UploadRequest = Body(
        ..., example={"GROUPROOM_NUM": 1, "MEMBER_NUM": 2}
    ),
    files: List[UploadFile] = File(...),
):
    try:
        # GROUPROOM_NUM, MEMBER_NUM 출력
        GROUPROOM_NUM = upload_request.GROUPROOM_NUM
        MEMBER_NUM = upload_request.MEMBER_NUM

        gcs_folder_path = f"rooms/{GROUPROOM_NUM}/{MEMBER_NUM}/"

        for file in files:
            upload_to_gcs(file.file, file.filename, gcs_folder_path)

        return {"message": "Files uploaded with JSON request successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")


@app.post("/bluedump/")
async def send_message(msg: Message, background_tasks: BackgroundTasks):
    temp_folder_path = "./temp"

    if os.path.exists(temp_folder_path):
        shutil.rmtree(temp_folder_path)
        print(f"{temp_folder_path}가 삭제되었습니다.")

    group_id = msg.groupID
    background_tasks.add_task(handle_background_tasks, group_id=group_id)
    return {"message": f"You sent groupID: {group_id}"}


# FastAPI 서버 실행 부분
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
