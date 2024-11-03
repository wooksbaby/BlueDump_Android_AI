import os
import shutil
import asyncio
import logging
import aiofiles
import aiofiles.os
from deepface import DeepFace
from utils import convert_to_jpg
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import cv2
import concurrent.futures


async def ensure_directory_exists(directory):
    """Ensure that the directory exists (async version)."""
    if not await aiofiles.os.path.exists(directory):
        await aiofiles.os.makedirs(directory)


async def convert_to_jpg(image_path):
    """이미지 파일을 JPG로 변환"""
    if not image_path.endswith(".jpg"):
        jpg_path = image_path.rsplit(".", 1)[0] + ".jpg"
        try:
            with Image.open(image_path) as img:
                rgb_img = img.convert("RGB")
                rgb_img.save(jpg_path, "JPEG")
            return jpg_path
        except Exception as e:
            raise
    return image_path


# DeepFace.verify를 스레드풀에서 실행하는 비동기 함수



async def classify_images(target_dir, image_dir, outputs):
    """이미지 디렉토리의 모든 이미지를 가져와서 타겟 얼굴을 찾습니다."""
    # 출력 디렉토리 확인 및 생성
    if not os.path.exists(outputs):
        os.makedirs(outputs)
        print(f"출력 디렉토리 '{outputs}'를 생성했습니다.")

    # 타겟 디렉토리 내의 이미지 목록 가져오기
    target_images_list = [os.path.join(target_dir, f) for f in os.listdir(target_dir)]
    image_file_list = [os.path.join(image_dir, f) for f in os.listdir(image_dir)]

    for target in target_images_list:
        for image in image_file_list:
            result = DeepFace.verify(
                img1_path=target,
                img2_path=image,
                model_name="Facenet",
                enforce_detection=False,
                distance_metric="euclidean_l2",
                detector_backend="retinaface",
                align=True
            )
            # 결과가 True인 경우 img2를 outputs에 target 이름의 폴더 아래에 저장합니다.
            if result['verified']: 
                # 타겟 이미지의 파일 이름을 추출
                target_name = os.path.splitext(os.path.basename(target))[0]
                target_output_dir = os.path.join(outputs, target_name)

                # 출력 디렉토리 확인 및 생성
                if not os.path.exists(target_output_dir):
                    os.makedirs(target_output_dir)
                    print(f"'{target_output_dir}'를 생성했습니다.")

                # img2를 해당 폴더로 복사
                shutil.copy(image, os.path.join(target_output_dir, os.path.basename(image)))
                print(f"'{image}'가 '{target_output_dir}'로 복사되었습니다.")

    