from passlib.context import CryptContext
import jwt
from fastapi import HTTPException
from PIL import Image
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def convert_to_jpg(image_path):
    """이미지 파일을 JPG로 변환"""
    if not image_path.endswith('.jpg'):
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')  # RGB로 변환
            rgb_img.save(jpg_path, 'JPEG')  # JPG 형식으로 저장
        return jpg_path
    return image_path  # 이미 JPG라면 원래 경로 반환
