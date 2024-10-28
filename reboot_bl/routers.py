from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Request
from gcs_controller import (
    upload_file_to_gcs,
    copy_profile_image_in_gcs,
    download_images_from_gcs,
    download_blobs,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import SessionLocal, get_db, get_async_db
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
)
from utils import verify_password, hash_password  # Assuming these functions exist
from sqlalchemy.orm import Session
from typing import List, Union
from bdconfig import bucket
from fastapi.responses import JSONResponse
from image_processing import classify_images
import asyncio


router = APIRouter()


@router.post("/upload")
async def upload_profile_images(
    grouproom_num: str = Form(...),  # 클라이언트에서 GROUPROOM_NUM을 문자열로 받음
    files: List[UploadFile] = File(...),
):

    urls = []  # 업로드된 파일의 URL을 저장할 리스트

    for file in files:
        # 파일 이름을 GCS에 저장할 경로로 설정 (GROUPROOM_NUM을 포함)
        destination_blob_name = f"rooms/{grouproom_num}/image/{file.filename}"  # 각 파일마다 고유한 경로 설정

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


@router.post("/uploaded_images", response_model=UploadedImagesResponse)
async def get_uploaded_images(request: UploadedImagesRequest):
    # GCS 버킷에서 해당 그룹룸의 이미지 경로 구성
    group_room_num = request.group_room_num
    prefix = f"rooms/{group_room_num}/image/"

    # 해당 경로의 모든 블롭(파일) 나열
    blobs = bucket.list_blobs(prefix=prefix)

    # 이미지 URL 리스트 생성
    image_urls = []
    for blob in blobs:
        # 공개 URL 생성
        image_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
        image_urls.append(image_url)

    # 이미지 URL 목록 반환
    return {"group_room_num": group_room_num, "image_urls": image_urls}


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
    )


@router.post("/joinroom")
async def join_room(request: JoinRoomRequest, db: Session = Depends(get_db)):
    # RoomMember 모델 인스턴스 생성 (가정)
    new_member = GroupDetail(
        GROUP_ROOM_NUM=request.group_room_num, MEMBER_NUM=request.member_num
    )
    # 현재 그룹의 모든 멤버 번호 가져오기
    members_in_group = (
        db.query(GroupDetail.MEMBER_NUM)
        .filter(GroupDetail.GROUP_ROOM_NUM == request.group_room_num)
        .all()
    )
    # 멤버 번호만 리스트로 추출
    member_nums = [member[0] for member in members_in_group]
    if request.member_num not in member_nums:  # 중복 추가 방지
        member_nums.append(request.member_num)
    try:
        # 세션에 추가
        db.add(new_member)
        db.commit()  # 변경 사항 커밋
        db.refresh(new_member)  # 새로 생성된 인스턴스 정보 업데이트
    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        raise HTTPException(status_code=500, detail="Failed to join room: " + str(e))

    # 성공 응답
    return JSONResponse(
        content={
            "success": True,
            "message": f"Member {request.member_num} added to room {request.group_room_num}.",
            "group_room_num": request.group_room_num,
            "member_nums": member_nums,  # 해당 그룹의 모든 멤버 번호 리스트 반환
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


# 최종적으로 classify_photos 함수 수정


@router.post("/classify_photos")
async def classify_photos(
    request: ClassifyPhotosRequest, db: AsyncSession = Depends(get_async_db)
):
    group_room_num = request.group_room_num
    target_directory = f"rooms/{group_room_num}/targets/"
    images_directory = f"rooms/{group_room_num}/image/"
    output_base_directory = f"rooms/{group_room_num}/output/"

    # GROUP_ROOM_NUM으로 GroupRoom을 조회
    result = await db.execute(
        select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
    )
    group_room = await result.scalar_one_or_none()

    if not group_room:
        raise await HTTPException(status_code=404, detail="Group room not found.")

    # CLASSIFIED_FINISH_FLAG를 ACTIVE로 변경
    group_room.CLASSIFIED_FINISH_FLAG = "ACTIVE"
    await db.commit()

    response = {"message": "분류를 시작합니다.", "group_room_num": group_room_num}

    async def background_task(group_room_num: int):
        async with get_async_db() as session:
            try:
                # 1. 이미지 다운로드
                print("down start")
                print(
                    f"down start: group_room_num: {group_room_num}, target_directory: {target_directory}, images_directory: {images_directory},"
                )

                await download_blobs(group_room_num)  # 비동기 다운로드 호출
                print("down end")

                # 2. DeepFace 모델 실행하여 사진 분류
                print("classify start")
                await classify_images(
                    target_directory, images_directory, output_base_directory
                )  # 비동기 분류 호출
                print("classify end")

                # 분류 완료 후 CLASSIFIED_FINISH_FLAG를 COMPLETED로 변경
                result = await session.execute(
                    select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
                )
                group_room_instance = result.scalar_one_or_none()

                if group_room_instance:
                    group_room_instance.CLASSIFIED_FINISH_FLAG = "COMPLETED"
                    await session.commit()
            except Exception as e:
                # 예외 발생 시 CLASSIFIED_FINISH_FLAG를 INACTIVE로 되돌리기
                result = await session.execute(
                    select(GroupRoom).filter(GroupRoom.GROUP_ROOM_NUM == group_room_num)
                )
                group_room_instance = result.scalar_one_or_none()

                if group_room_instance:
                    group_room_instance.CLASSIFIED_FINISH_FLAG = "INACTIVE"
                    await session.commit()
                print(f"Error during image classification: {e}")

    # 비동기 작업 생성
    asyncio.create_task(background_task(group_room_num))
    return response




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
