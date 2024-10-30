import os
import shutil
import asyncio
import logging
import aiofiles
import aiofiles.os
from deepface import DeepFace
from utils import convert_to_jpg
from PIL import Image
import tensorflow as tf



# TensorFlow GPU 설정
physical_devices = tf.config.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

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
    if not image_path.endswith('.jpg'):
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        try:
            with Image.open(image_path) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(jpg_path, 'JPEG')
                logger.info(f"Converted {image_path} to {jpg_path}")
            return jpg_path
        except Exception as e:
            logger.error(f"Error converting {image_path} to JPG: {e}")
            raise
    return image_path

async def deepface_verify_async(img1_path, img2_path):
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(
            None, 
            lambda: DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name="Facenet",
                distance_metric="euclidean",
                detector_backend="retinaface",
                enforce_detection=True,
                align=True
            )
        )
    except Exception as e:
        logger.error(f"Error during DeepFace verification between {img1_path} and {img2_path}: {e}")
        raise
async def classify_images_with_options(group_room_num: int):
    """타겟 이미지를 기준으로 다양한 옵션으로 이미지 분류 및 저장"""
    logger.info("Starting image classification process...")

    # 디렉토리 경로 설정
    target_directory = f"cloud-bucket-bluedump/rooms/{group_room_num}/targets"
    images_directory = f"cloud-bucket-bluedump/rooms/{group_room_num}/images"
    output_base_directory = f"cloud-bucket-bluedump/rooms/{group_room_num}/outputs"

    # 타겟 및 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [
        await convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)
    ]
    images = [
        await convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)
    ]

    matched_count = 0
    similarities = []

    # 결과가 저장될 디렉토리 설정
    await ensure_directory_exists(output_base_directory)

    for image in images:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]
            person_directory = os.path.join(output_base_directory, person_name)
            await ensure_directory_exists(person_directory)

            try:
                # DeepFace로 얼굴 비교 (GPU 사용)
                result = await deepface_verify_async(target_image, image)

                if result["verified"]:
                    # 매칭된 이미지를 비동기적으로 복사
                    await asyncio.get_event_loop().run_in_executor(
                        None, shutil.copy, image, person_directory
                    )
                    matched_count += 1
                    similarities.append(result['distance'])
                    logger.info(f"Match found: {person_name} in {os.path.basename(image)}")
                else:
                    logger.info(f"No match for {person_name} in {os.path.basename(image)}")

            except Exception as e:
                logger.error(f"Error processing image {os.path.basename(image)}: {e}")

    logger.info(f"Classification complete: {matched_count} matches found. Similarities: {similarities}")

    # outputs 폴더를 GCS에 업로드
    from gcs_controller import upload_folder_to_gcs
    await upload_folder_to_gcs(output_base_directory, f"rooms/{group_room_num}/outputs/")
