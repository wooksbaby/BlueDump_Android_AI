from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    Form,
    BackgroundTasks,
)
from gcs_controller import (
    upload_file_to_gcs,
    copy_profile_image_in_gcs,
    download_blobs,
    upload_folder_to_gcs,
)
import os
from model import GroupRoom, GroupDetail, Member  # 모델이 정의된 파일을 import
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import SessionLocal, get_db, get_async_db, AsyncSessionLocal
from model import Member, GroupRoom, GroupDetail
from schemas import (
    LoginRequest,
    LoginResponse,
    SignUpResponse,
    ErrorResponse,
    CreateRoomResponse,
    CreateRoomRequest,
    JoinRoomRequest,
    RoomDetailResponse,
    MemberDetail,
    GroupRoomStatusResponse,
    GroupRoomRequest,
    UploadedImagesRequest,
    UploadedImagesResponse,
    MemberNumRequest,
    ClassifyPhotosRequest,
    UpdateStatusRequest,
    TestClassifyPhotosRequest,
    UploadedImages,
    MemberImages,
)
import shutil

# from utils import verify_password, hash_password, cur_dir  # Assuming these functions exist
from sqlalchemy.orm import Session
from typing import List, Union
from bdconfig import bucket
from fastapi.responses import JSONResponse
from image_processing import classify_images
import asyncio
from sqlalchemy import exists
import threading


router = APIRouter()


@router.post("/upload")
async def upload_profile_images(
    grouproom_num: str = Form(...),  # 클라이언트에서 GROUPROOM_NUM을 문자열로 받음
    member_num: int = Form(...),  # 클라이언트에서 MEMBER_NUM을 정수로 받음
    files: List[UploadFile] = File(...),
):

    urls = []  # 업로드된 파일의 URL을 저장할 리스트

    for file in files:
        # 파일 이름을 GCS에 저장할 경로로 설정 (GROUPROOM_NUM을 포함)
        destination_blob_name = f"rooms/{grouproom_num}/image/{member_num}/{file.filename}"  # 각 파일마다 고유한 경로 설정

        # 파일 업로드 처리
        upload_result = await upload_file_to_gcs(file, destination_blob_name)

        if upload_result:
            # 파일이 성공적으로 업로드된 경우, URL을 리스트에 추가
            public_url = (
                f"https://storage.googleapis.com/{bucket.name}/{destination_blob_name}"
            )
            urls.append(public_url)
        else:
            return {"message": "Failed to upload one or more images."}

    return {"message": "Images uploaded successfully", "urls": urls}


@router.post("/uploaded_images", response_model=UploadedImages)
async def get_uploaded_images(request: UploadedImagesRequest):
    # GCS 버킷에서 해당 그룹룸의 이미지 경로 구성
    group_room_num = request.group_room_num
    member_num = request.member_num

    prefix = f"rooms/{group_room_num}/image/{member_num}/"

    # 해당 경로의 모든 블롭(파일) 나열
    blobs = bucket.list_blobs(prefix=prefix)

    # 이미지 URL 리스트 생성
    image_urls = []
    for blob in blobs:
        # 공개 URL 생성
        image_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
        image_urls.append(image_url)

    # 이미지 URL 목록 반환
    return {
        "group_room_num": group_room_num,
        "member_num": member_num,
        "image_urls": image_urls,
    }


@router.post("/classified_images", response_model=UploadedImagesResponse)
async def get_classified_images(
    request: UploadedImagesRequest,
    db: Session = Depends(get_db),  # DB 세션을 사용해 GROUP_ROOM_OPTION 값 확인
):
    # 요청에서 그룹룸 번호와 멤버 번호 추출
    group_room_num = request.group_room_num
    member_num = request.member_num

    # 그룹룸 옵션 확인
    group_room = db.query(GroupRoom).filter_by(GROUP_ROOM_NUM=group_room_num).first()

    if group_room is None:
        return {"message": "Group room not found."}

    # 옵션에 따라 prefix 설정
    if group_room.GROUP_ROOM_OPTION:  # True인 경우 모든 멤버 결과 반환
        prefix = f"rooms/{group_room_num}/outputs/"
    else:  # False인 경우 특정 멤버 결과만 반환
        prefix = f"rooms/{group_room_num}/outputs/{member_num}/"

    # 해당 경로의 모든 블롭(파일) 나열
    blobs = bucket.list_blobs(prefix=prefix)

    # 멤버별 이미지 URL 딕셔너리 생성
    member_images = {}
    for blob in blobs:
        # 확장자가 .jpg인 파일만 추가
        if blob.name.lower().endswith((".jpg", ".jpeg", ".png")):
            # /로 분리하여 유저 넘버 추출
            parts = blob.name.split("/")
            blob_member_num = parts[3]  # results 다음의 유저넘버 부분 추출
            image_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"

            # 각 멤버에 대한 이미지 URL 리스트에 추가
            if blob_member_num not in member_images:
                member_images[blob_member_num] = []  # 새 멤버 초기화
            member_images[blob_member_num].append(image_url)

    # 응답 형식 변환
    member_images_list = []

    for member_id, images in member_images.items():
        try:
            # member_id를 정수로 변환 시도
            member_id_int = int(member_id)
            
            # 각 멤버에 대한 URL과 닉네임을 DB에서 가져오기
            member_data = db.query(Member).filter_by(MEMBER_NUM=member_id_int).first()

            # member_url과 nickname이 존재하면 가져오고, 없으면 None으로 설정
            member_profile_url = (
                member_data.PROFILE_PATH if member_data else None
            )
            member_nickname = (
                member_data.MEMBER_NICKNAME if member_data else None
            )

            member_images_list.append(
                {
                    "member_id": member_id_int,
                    "images": images,
                    "member_url": member_profile_url,
                    "nickname": member_nickname,
                }
            )
        except ValueError:
            # 정수 변환 실패 시 로깅 또는 다른 처리를 할 수 있습니다.
            print(f"Invalid member_id: {member_id}. Skipping...")

    # 최종 응답 반환
    return {
        "group_room_num": group_room_num,
        "member_images": member_images_list,  # 요청한 형식으로 응답 구성
    }


# @router.post("/classified_images", response_model=UploadedImagesResponse)
# async def get_classified_images(
#     request: UploadedImagesRequest,
#     db: Session = Depends(get_db)  # DB 세션을 사용해 GROUP_ROOM_OPTION 값 확인
# ):
#     # 요청에서 그룹룸 번호와 멤버 번호 추출
#     group_room_num = request.group_room_num
#     member_num = request.member_num

#     # 그룹룸 옵션 확인
#     group_room = db.query(GroupRoom).filter_by(GROUP_ROOM_NUM=group_room_num).first()

#     if group_room is None:
#         return {"message": "Group room not found."}

#     # 옵션에 따라 prefix 설정
#     if group_room.GROUP_ROOM_OPTION:  # True인 경우 모든 멤버 결과 반환
#         prefix = f"rooms/{group_room_num}/results/"
#     else:  # False인 경우 특정 멤버 결과만 반환
#         prefix = f"rooms/{group_room_num}/results/{member_num}/"

#     # 해당 경로의 모든 블롭(파일) 나열
#     blobs = bucket.list_blobs(prefix=prefix)

#     # 이미지 URL 리스트 생성
#     image_urls = []
#     for blob in blobs:
#         # 확장자가 .jpg인 파일만 추가
#         if blob.name.lower().endswith(".jpg"):
#             image_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
#             image_urls.append(image_url)

#     # 이미지 URL 목록 반환
#     return {
#         "group_room_num": group_room_num,
#         "member_num": member_num,
#         "image_urls": image_urls
#     }


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.MEMBER_ID == request.username).first()

    # 아이디가 없는 경우 처리
    if not member:
        return LoginResponse(
            success=False,
            error_msg="Username does not exist",
            error_type="authentication_error",
        )

    # 비밀번호 비교
    if request.password != member.MEMBER_PW:
        return LoginResponse(
            success=False,
            error_msg="Invalid password",
            error_type="authentication_error",
        )

    # 로그인 성공 처리
    return LoginResponse(
        success=True,
        member_num=member.MEMBER_NUM,
        nickname=member.MEMBER_NICKNAME,
        profileUrl=member.PROFILE_PATH,
    )


@router.post("/signup", response_model=Union[SignUpResponse, ErrorResponse])
async def signup(
    nickname: str = Form(None),  # Form에서 직접 가져오기
    username: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None),
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 비어 있는 값 확인
    if not nickname or not username or not password or not confirm_password:
        return ErrorResponse(
            success=False,
            error_msg="All fields are required.",
            error_type="ValidationError",
        )

    # 비밀번호 확인
    if password != confirm_password:
        return ErrorResponse(
            success=False,
            error_msg="Passwords do not match.",
            error_type="ValidationError",
        )

    # MEMBER_ID 중복 확인
    existing_member = db.query(Member).filter(Member.MEMBER_ID == username).first()
    if existing_member:
        return ErrorResponse(
            success=False,
            error_msg="Username already exists.",
            error_type="ConflictError",
        )

    # 사용자 생성
    new_member = Member(
        MEMBER_ID=username,
        MEMBER_PW=password,
        MEMBER_NICKNAME=nickname,
    )

    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)  # 새로운 멤버 정보를 가져옵니다.
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_msg": "Failed to create user: " + str(e),
                "error_type": "DatabaseError",
            },
        )

    # GCS에 이미지 업로드
    image_path = f"profile/{new_member.MEMBER_NUM}.jpg"
    upload_result = await upload_file_to_gcs(profile_image, image_path)

    # 이미지 업로드 결과 체크
    if not upload_result:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_msg": "Failed to upload image to GCS.",
                "error_type": "UploadError",
            },
        )

    # PROFILE_PATH 추가
    base_url = "https://storage.googleapis.com/cloud-bucket-bluedump/"
    new_member.PROFILE_PATH = f"{base_url}{image_path}"  # 전체 URL 추가
    try:
        db.commit()  # 변경사항 커밋
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_msg": "Failed to update profile path: " + str(e),
                "error_type": "DatabaseError",
            },
        )

    return SignUpResponse(
        success=True,
        message="User created successfully",
        member_num=new_member.MEMBER_NUM,
    )


@router.post("/createroom", response_model=CreateRoomResponse)
async def create_room(
    room_data: CreateRoomRequest,
    db: Session = Depends(get_db),
):

    # 불리언 값을 TINYINT로 변환
    tinyint_option = 1 if room_data.option else 0  # True -> 1, False -> 0

    # 그룹방 생성
    new_group_room = GroupRoom(
        MEMBER_NUM=room_data.member_num,
        GROUP_ROOM_NAME=room_data.group_room_name,
        GROUP_ROOM_OPTION=tinyint_option,
    )

    try:
        # 그룹방 추가 및 커밋
        db.add(new_group_room)
        db.commit()
        db.refresh(new_group_room)  # 새로운 그룹룸의 정보를 갱신

        # 그룹 디테일에 방 생성자 추가
        group_detail_entry = GroupDetail(
            GROUP_ROOM_NUM=new_group_room.GROUP_ROOM_NUM,
            MEMBER_NUM=room_data.member_num,  # 방 만든 사람의 MEMBER_NUM
        )
        db.add(group_detail_entry)
        db.commit()
        db.refresh(group_detail_entry)  # 새로운 디테일 정보 갱신
        # GCS에서 프로필 사진 복사
        source_blob_name = f"profile/{room_data.member_num}.jpg"  # 원본 이미지 경로
        destination_blob_name = f"rooms/{new_group_room.GROUP_ROOM_NUM}/targets/{room_data.member_num}.jpg"  # 복사할 경로

        copy_profile_image_in_gcs(source_blob_name, destination_blob_name)

    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        raise HTTPException(
            status_code=500, detail="Failed to create group room: " + str(e)
        )

    return CreateRoomResponse(
        success=True,
        group_room_num=new_group_room.GROUP_ROOM_NUM,  # GROUP_ROOM_NUM 반환
        option=room_data.option,  # GROUP_ROOM_OPTION 반환
    )


@router.post("/joinroom")
async def join_room(request: JoinRoomRequest, db: Session = Depends(get_db)):
    # 이미 해당 멤버가 그룹에 있는지 확인
    is_member_exists = db.query(
        exists().where(
            (GroupDetail.GROUP_ROOM_NUM == request.group_room_num)
            & (GroupDetail.MEMBER_NUM == request.member_num)
        )
    ).scalar()

    if is_member_exists:
        return JSONResponse(
            content={
                "success": False,
                "message": f"Member {request.member_num} already in room {request.group_room_num}.",
            }
        )

    # 멤버가 없는 경우 새로 추가
    new_member = GroupDetail(
        GROUP_ROOM_NUM=request.group_room_num, MEMBER_NUM=request.member_num
    )

    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        # GCS에서 프로필 사진 복사
        source_blob_name = f"profile/{request.member_num}.jpg"  # 원본 이미지 경로
        destination_blob_name = f"rooms/{request.group_room_num}/targets/{request.member_num}.jpg"  # 복사할 경로
        copy_profile_image_in_gcs(source_blob_name, destination_blob_name)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to join room: " + str(e))

    # 멤버 리스트 다시 가져오기
    members_in_group = (
        db.query(GroupDetail.MEMBER_NUM)
        .filter(GroupDetail.GROUP_ROOM_NUM == request.group_room_num)
        .all()
    )
    member_nums = [member[0] for member in members_in_group]

    return JSONResponse(
        content={
            "success": True,
            "message": f"Member {request.member_num} added to room {request.group_room_num}.",
            "group_room_num": request.group_room_num,
            "member_nums": member_nums,
        }
    )


@router.get("/roomdetail", response_model=RoomDetailResponse)
async def get_room_detail(group_room_num: int, db: Session = Depends(get_db)):

    # 해당 그룹 방의 멤버 정보 가져오기
    members_in_group = (
        db.query(GroupDetail).filter(GroupDetail.GROUP_ROOM_NUM == group_room_num).all()
    )

    # 멤버의 상세 정보를 리스트로 변환
    members = [
        MemberDetail(
            member_num=member.MEMBER_NUM,
            nickname=member.member.MEMBER_NICKNAME,  # 관계 설정에 따라 접근
            profile_path=member.member.PROFILE_PATH,  # 프로필 이미지 경로
        )
        for member in members_in_group
    ]

    # 초대 링크 URL 생성 (리다이렉트 페이지를 호출하는 URL로 설정)
    BASE_URL = "http://34.80.78.104:8000"
    invite_url = f"{BASE_URL}/invite/{group_room_num}"

    return RoomDetailResponse(
        group_room_num=group_room_num, group_room_url=invite_url, members=members
    )


@router.post("/grouproom/status", response_model=GroupRoomStatusResponse)
async def get_group_room_status(
    request: GroupRoomRequest, db: Session = Depends(get_db)
):
    """
    주어진 그룹 방 번호에 대한 상태값을 반환하는 엔드포인트
    """
    group_room = (
        db.query(GroupRoom)
        .filter(GroupRoom.GROUP_ROOM_NUM == request.group_room_num)
        .first()
    )

    if not group_room:
        raise HTTPException(status_code=404, detail="Group room not found")

    return GroupRoomStatusResponse(
        group_room_num=group_room.GROUP_ROOM_NUM,
        classified_finish_flag=group_room.CLASSIFIED_FINISH_FLAG,
    )


#### 리턴 어떻게 줄지 생각해보자


@router.post("/member/group-rooms", response_model=List[dict])
async def get_member_group_rooms(
    request: MemberNumRequest, db: Session = Depends(get_db)
):
    """
    주어진 회원 번호에 대해 참가하고 있는 모든 그룹 방의 번호와 이름을 반환하는 엔드포인트
    """
    # TB_GROUP_DETAIL과 TB_GROUPROOM 테이블을 조인하여 해당 회원이 속한 모든 그룹 방 조회
    member_groups = (
        db.query(GroupDetail.GROUP_ROOM_NUM, GroupRoom.GROUP_ROOM_NAME)
        .join(GroupRoom, GroupDetail.GROUP_ROOM_NUM == GroupRoom.GROUP_ROOM_NUM)
        .filter(GroupDetail.MEMBER_NUM == request.member_num)
        .distinct()
        .all()
    )

    # 그룹 방 정보 리스트 생성
    group_rooms = [
        {
            "group_room_num": group.GROUP_ROOM_NUM,
            "group_room_name": group.GROUP_ROOM_NAME,
        }
        for group in member_groups
    ]

    # 회원이 참여하는 그룹룸이 없어도 빈 배열 반환 (상태 코드 200)
    return group_rooms


# 그룹룸 상태 업데이트 엔드포인트 (POST 메소드)


@router.post("/group-room/update-status")
async def update_group_room_status(
    request: UpdateStatusRequest, db: AsyncSession = Depends(get_async_db)
):
    # 가능한 상태값 리스트
    valid_statuses = ["INACTIVE", "ACTIVE", "COMPLETED"]

    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be one of INACTIVE, ACTIVE, or COMPLETED",
        )

    # 해당 grouproom_num 검색
    result = await db.execute(
        select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == request.group_room_num)
    )
    group_room = result.scalars().first()  # 첫 번째 결과를 가져옵니다.

    # 그룹룸 존재 여부 확인
    if not group_room:
        raise HTTPException(status_code=404, detail="Group room not found")

    # 상태 업데이트
    group_room.CLASSIFIED_FINISH_FLAG = request.status
    await db.commit()  # 변경 사항 저장

    return {"grouproom_num": request.group_room_num, "updated_status": request.status}


@router.post("/test_classify_photos")
async def test_classify_photos(
    request: TestClassifyPhotosRequest, db: AsyncSession = Depends(get_async_db)
):
    # 요청으로부터 group_room_num 가져오기
    group_room_num = request.group_room_num
    delay = request.delay

    # 해당 group_room_num 검색
    result = await db.execute(
        select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
    )
    group_room = result.scalars().first()  # 첫 번째 결과를 가져옵니다.

    # 그룹룸 존재 여부 확인
    if not group_room:
        raise HTTPException(status_code=404, detail="Group room not found")

    # 그룹룸의 CLASSIFIED_FINISH_FLAG를 'ACTIVE'로 변경
    group_room.CLASSIFIED_FINISH_FLAG = "ACTIVE"
    await db.commit()  # 변경사항을 커밋합니다.

    # 즉시 응답
    response = {"message": f"Received group_room_num: {group_room_num}"}

    # 비동기로 20초 대기 후 플래그 변경
    asyncio.create_task(
        update_flag_after_delay(group_room_num, delay)
    )  # group_room_num을 전달

    return response


async def update_flag_after_delay(group_room_num: int, delay: int):
    # 비동기 세션을 새로 생성합니다.
    async with AsyncSessionLocal() as db:  # AsyncSessionLocal이 설정된 곳에서 가져옵니다.
        # 지연 후에 플래그 업데이트 작업을 수행합니다.
        await asyncio.sleep(delay)

        # GroupRoom을 선택합니다.
        result = await db.execute(
            select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
        )
        group_room = result.scalars().first()

        if group_room is None:
            return {"error": "Group room not found"}

        # 여기에 플래그를 업데이트하는 로직 추가
        group_room.CLASSIFIED_FINISH_FLAG = (
            "COMPLETED"  # 예시로 플래그를 변경합니다. (ACTIVE -> INACTIVE로 변경)
        )

        await db.commit()  # 커밋하여 변경 사항을 저장합니다.


@router.post("/classify_photos")
async def classify_photos(
    request: ClassifyPhotosRequest,
    # background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),  # 비동기 세션 사용
):
    group_room_num = request.group_room_num

    # GROUP_ROOM_NUM으로 GroupRoom을 조회
    result = await db.execute(
        select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
    )
    group_room = result.scalar_one_or_none()

    if not group_room:
        raise HTTPException(status_code=404, detail="Group room not found.")

    # CLASSIFIED_FINISH_FLAG를 ACTIVE로 변경
    group_room.CLASSIFIED_FINISH_FLAG = "ACTIVE"
    await db.commit()

    # 응답 메시지
    response = {"message": f"{group_room_num}번방 분류를 시작합니다."}

    asyncio.create_task(background_task(group_room_num))

    # 응답 즉시 반환
    return response

    # # 백그라운드 작업을 BackgroundTasks로 수행
    # asyncio.create_task(
    # background_task(group_room_num), db)  # db 인자 전달

    # return response


async def background_task(group_room_num: int):
    async with AsyncSessionLocal() as db:  # AsyncSessionLocal이 설정된 곳에서 가져옵니다.

        print("background task started")
    # async_session = AsyncSessionLocal
    # 트랜잭션 시작
    try:
        # 이미지 다운로드
        await download_blobs(group_room_num)

        # 다운로드한 이미지 파일 목록을 가져옴
        cur_dir = os.getcwd()
        target_dir = os.path.join(cur_dir, str(group_room_num), "targets")
        image_dir = os.path.join(cur_dir, str(group_room_num), "image")
        outputs = os.path.join(cur_dir, str(group_room_num), "outputs")

        # 이미지 분류 실행
        await classify_images(target_dir, image_dir, outputs)
        print("분류 완료")

        # 새로운 비동기 세션을 열어 데이터베이스 작업 수행
        # GROUP_ROOM_NUM을 기준으로 그룹룸 조회
        result = await db.execute(
            select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
        )
        group_room = result.scalar_one_or_none()

        # GCS에 업로드할 폴더 경로 설정
        destination_blob_prefix = f"rooms/{group_room_num}/outputs"
        await upload_folder_to_gcs(bucket, outputs, destination_blob_prefix)

        if group_room:
            # 상태를 COMPLETED로 변경
            group_room.CLASSIFIED_FINISH_FLAG = "COMPLETED"
            await db.commit()  # 변경 사항 커밋
            print(f"그룹룸 {group_room_num}의 상태를 'COMPLETED'로 변경했습니다.")
        else:
            print(f"그룹룸 {group_room_num}을 찾을 수 없습니다.")

        # 그룹 룸 폴더 삭제
        await delete_group_room_folder(group_room_num)
        print(f"그룹룸 {group_room_num}의 폴더를 삭제했습니다.")

    except Exception as e:
        print(f"Error during background task: {e}")


async def delete_group_room_folder(group_room_num):
    """현재 작업 디렉토리에서 지정된 그룹룸 번호에 해당하는 폴더를 삭제합니다."""
    # 현재 작업 디렉토리 가져오기
    cur_dir = os.getcwd()
    folder_path = os.path.join(cur_dir, str(group_room_num))

    # 폴더가 존재하는지 확인
    if os.path.exists(folder_path):
        # 폴더 삭제
        await asyncio.to_thread(shutil.rmtree, folder_path)
        print(f"폴더 '{folder_path}'가 삭제되었습니다.")
    else:
        print(f"폴더 '{folder_path}'가 존재하지 않습니다.")
