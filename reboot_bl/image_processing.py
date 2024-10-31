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


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ensure_directory_exists(directory):
    """Ensure that the directory exists (async version)."""
    if not await aiofiles.os.path.exists(directory):
        await aiofiles.os.makedirs(directory)
        logger.info(f"Directory created: {directory}")


async def convert_to_jpg(image_path):
    """이미지 파일을 JPG로 변환"""
    if not image_path.endswith(".jpg"):
        jpg_path = image_path.rsplit(".", 1)[0] + ".jpg"
        try:
            with Image.open(image_path) as img:
                rgb_img = img.convert("RGB")
                rgb_img.save(jpg_path, "JPEG")
                logger.info(f"Converted {image_path} to {jpg_path}")
            return jpg_path
        except Exception as e:
            logger.error(f"Error converting {image_path} to JPG: {e}")
            raise
    return image_path


# DeepFace.verify를 스레드풀에서 실행하는 비동기 함수



def deepface_verify(img1, img2):
    """Verify if two images are of the same person using DeepFace."""
    
    # 파일 경로 확인
    if not os.path.exists(img1):
        print(f"Error: img1 파일이 존재하지 않습니다: {img1}")
        return False
    if not os.path.exists(img2):
        print(f"Error: img2 파일이 존재하지 않습니다: {img2}")
        return False

    try:
        # DeepFace 비교 실행
        print(f"Comparing images:\n img1: {img1}\n img2: {img2}")
        result = DeepFace.verify(
            img1_path=img1,
            img2_path=img2,
            model_name="Facenet",
            distance_metric="euclidean",
            detector_backend="mtcnn",  # 또는 "opencv" 사용 가능
            enforce_detection=False,
            align=True,
        )
        
        print(f"Comparison result: {result['verified']}")
        return result["verified"]  # 비교 결과 반환

    except Exception as e:
        print(f"Error processing images {img1} and {img2}: {e}")
        return False  # 실패 시 False 반환
def classify_images(target_dir, image_dir, outputs):
    target_images = [os.path.join(target_dir, f) for f in os.listdir(target_dir)]
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_image = {executor.submit(deepface_verify, image, target_image): (image, target_image) for image in image_files for target_image in target_images}
        
        for future in concurrent.futures.as_completed(future_to_image):
            image, target_image = future_to_image[future]
            try:
                result = future.result()
                if result:
                    print(f"{image}와 {target_image}는 같은 사람입니다.")
                else:
                    print(f"{image}와 {target_image}는 다른 사람입니다.")
            except Exception as exc:
                print(f"{image}와 {target_image} 비교 중 오류 발생: {exc}")
            

    

def classify_images_with_options(target_dir, image_dir, outputs, detector_backend='opencv'):
    # 타겟 이미지와 비교할 대상 이미지 목록
    target_images = [os.path.join(target_dir, f) for f in os.listdir(target_dir)]
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir)]

    for image in image_files:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]
            person_directory = os.path.join(outputs, person_name)  # 각 타겟별 디렉토리 생성

            # 디렉토리 생성
            if not os.path.exists(person_directory):
                os.makedirs(person_directory)

            try:
                # 얼굴 위치 감지
                detections = DeepFace.extract_faces(img_path=image, detector_backend=detector_backend)

                # 감지된 얼굴이 있을 경우 각 얼굴을 타겟과 비교
                if detections:
                    img = Image.open(image)
                    for idx, region in enumerate(detections):
                        # 얼굴 영역 잘라내기
                        cropped_face = img.crop((region['x'], region['y'], region['x'] + region['w'], region['y'] + region['h']))
                        cropped_face_path = os.path.join(person_directory, f"{os.path.basename(image).rsplit('.', 1)[0]}_face_{idx}.jpg")
                        cropped_face.save(cropped_face_path)

                        # 타겟 이미지와 비교하는 부분 추가
                        match_result = DeepFace.verify(cropped_face_path, target_image, detector_backend=detector_backend)
                        print(f"{os.path.basename(image)}의 얼굴과 {os.path.basename(target_image)} 비교 결과: {match_result}")

                else:
                    print(f"{os.path.basename(image)}에서 얼굴을 감지하지 못했습니다.")

            except Exception as e:
                print(f"{os.path.basename(image)}에서 얼굴을 감지하는 중 오류 발생: {e}")