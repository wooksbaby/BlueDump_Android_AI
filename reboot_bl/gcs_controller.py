import os
from bdconfig import bucket  # 전역 객체 불러오기
from fastapi import UploadFile, HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

executor = ThreadPoolExecutor()
def ensure_directory_exists(directory):
    """Ensure that a directory exists; if not, create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)

# 환경 변수 설정
async def copy_profile_image_in_gcs(source_blob_name: str, destination_blob_name: str):
    """GCS에서 프로필 이미지를 복사하는 함수."""
    source_blob = bucket.blob(source_blob_name)

    try:
        await asyncio.get_running_loop().run_in_executor(
            executor, bucket.copy_blob, source_blob, bucket, destination_blob_name
        )
        print(f"Copied {source_blob_name} to {destination_blob_name}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to copy profile image: {str(e)}"
        )


async def upload_file_to_gcs(file: UploadFile, destination_blob_name: str) -> bool:
    blob = bucket.blob(destination_blob_name)

    try:
        await asyncio.get_running_loop().run_in_executor(
            executor, blob.upload_from_file, file.file, file.content_type
        )
        return True
    except Exception as e:
        print(f"An error occurred while uploading to GCS: {e}")
        return False


async def upload_local_file_to_gcs(file_path: str, gcs_blob_path: str) -> None:
    """비동기로 단일 파일을 GCS에 업로드합니다."""
    blob = bucket.blob(gcs_blob_path)
    loop = asyncio.get_event_loop()

    await loop.run_in_executor(None, blob.upload_from_filename, file_path)


async def upload_folder_to_gcs(local_folder_path: str, group_room_num: int) -> None:
    """로컬 폴더를 GCS에 비동기로 업로드합니다."""
    destination_blob_prefix = f"rooms/{group_room_num}/outputs"
    tasks = []

    # 로컬 폴더의 파일을 순회합니다.
    for root, _, files in os.walk(local_folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            # GCS의 경로를 생성합니다.
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            gcs_blob_path = os.path.join(destination_blob_prefix, relative_path)

            # 비동기 업로드 작업을 추가합니다.
            tasks.append(upload_local_file_to_gcs(local_file_path, gcs_blob_path))

    # 모든 비동기 업로드 작업을 대기합니다.
    await asyncio.gather(*tasks)
    print("All files uploaded successfully.")


def download_blob(blob, destination_file_name):
    """Download a blob from GCS synchronously and convert to JPEG if it's an image."""
    try:
        # 다운로드할 파일의 디렉토리 확인 및 생성
        ensure_directory_exists(os.path.dirname(destination_file_name))

        # Blob을 다운로드
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded {blob.name} to {destination_file_name}")

        # 이미지 확장자 확인
        _, ext = os.path.splitext(destination_file_name)
        image_extensions = {'.png', '.bmp', '.gif', '.tiff', '.webp', '.jpg', '.jfif', '.svg', '.ico', '.raw', '.heif', '.heic'}

        # 이미지 파일이면 JPEG로 변환
        if ext.lower() in image_extensions:
            print("this file is image")
            # convert_to_jpeg(destination_file_name)  # 동기 JPEG 변환 함수 호출
        # else:
            # print(f"{destination_file_name} is not an image file.")

    except Exception as e:
        print(f"Error downloading {blob.name}: {e}")

def convert_to_jpeg(file_path):
    """Convert the given image file to JPEG format."""
    try:
        # 이미지 파일 열기
        with Image.open(file_path) as img:
            jpeg_file_path = os.path.splitext(file_path)[0] + '_converted.jpeg'
            img.convert('RGB').save(jpeg_file_path, 'JPEG')
            print(f"Converted {file_path} to {jpeg_file_path}")

            # 원본 파일 삭제 (옵션)
            # os.remove(file_path)

    except Exception as e:
        print(f"Error converting {file_path} to JPEG: {e}")

def download_blobs(group_room_num):
    print("download_blobs 함수 실행")
    """Download all blobs for a group room synchronously."""
    prefix = f"rooms/{group_room_num}/"
    current_directory = os.getcwd()

    # targets와 images 폴더 설정
    destination_folders = {
        "targets": os.path.join(current_directory, str(group_room_num), "targets"),
        "image": os.path.join(current_directory, str(group_room_num), "image"),
    }

    # Ensure the destination folders exist
    for folder in destination_folders.values():
        ensure_directory_exists(folder)

    blobs = bucket.list_blobs(prefix=prefix)

    # 동기 다운로드 작업 수행
    for blob in blobs:
        if blob.name.endswith("/"):
            print(f"Skipping directory: {blob.name}")
            continue

        # 저장할 폴더 결정
        destination_folder = destination_folders["targets"] if "targets/" in blob.name else destination_folders["image"]
        local_file_name = blob.name.split("/")[-1]
        local_file_path = os.path.join(destination_folder, local_file_name)

        print(f"Downloading {blob.name} to {local_file_path}...")
        download_blob(blob, local_file_path)  # 동기 다운로드 함수 호출

    print("All downloads completed.")