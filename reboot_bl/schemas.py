from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class MemberCreate(BaseModel):
    member_id: str
    member_pw: str
    member_nickname: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    error_msg: Optional[str] = None
    error_type: Optional[str] = None
    member_num: Optional[int] = None
    nickname: Optional[str] = None
    profileUrl: Optional[str] = None


class SignUpRequest(BaseModel):
    nickname: str = Field(..., example="3조핑")
    username: str = Field(..., example="wooksbaby")
    password: str = Field(..., example="0738asdf")
    confirm_password: str = Field(..., example="0738asdf")


class SignUpResponse(BaseModel):
    success: bool
    message: str
    member_num: int  # 생성된 사용자 번호 추가


class ErrorResponse(BaseModel):
    success: bool
    error_msg: str
    error_type: str


# 요청 데이터 모델 정의
class CreateRoomRequest(BaseModel):
    member_num: int
    group_room_name: str
    option: bool  # 두 개의 옵션 중 하나만 선택


# 응답 데이터 모델 정의
class CreateRoomResponse(BaseModel):
    success: bool
    group_room_num: int
    option: bool  
    # group_room_url: str  # 필요시 사용할 수 있도록 주석 처리


class JoinRoomRequest(BaseModel):
    member_num: int  # 참가하는 멤버 번호
    group_room_num: int

class MemberDetail(BaseModel):
    member_num: int
    nickname: str
    profile_path: str  # 프로필 이미지 경로


class RoomDetailResponse(BaseModel):
    group_room_num: int
    group_room_url: str
    members: List[MemberDetail] # 멤버 번호의 리스트

class GroupRoomRequest(BaseModel):
    group_room_num: int

class GroupRoomStatusResponse(BaseModel):
    group_room_num: int
    classified_finish_flag: str

# 업로드된 이미지 응답 모델

class UploadedImagesRequest(BaseModel):
    group_room_num: int
    member_num: int

class MemberImages(BaseModel):
    member_id: int
    member_url: str
    nickname : str
    images: List[str]

class UploadedImagesResponse(BaseModel):
    group_room_num: int

    member_images: List[MemberImages]  # Changed to a list of MemberImages



    
class UploadedImages(BaseModel):
    group_room_num: int
    member_num: int
    image_urls: List[str]  # Changed to a list of MemberImages

class MemberNumRequest(BaseModel):

    member_num: int


class TestClassifyPhotosRequest(BaseModel):
    group_room_num: int
    delay: int

class ClassifyPhotosRequest(BaseModel):
    group_room_num: int
    
class UpdateStatusRequest(BaseModel):
    group_room_num: int
    status: str
