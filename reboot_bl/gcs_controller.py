import os
from bdconfig import bucket  # 전역 객체 불러오기
from fastapi import UploadFile, HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()
from image_processing import ensure_directory_exists


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


async def download_folder_from_gcs(gcs_folder_path, local_folder_path):
    blobs = list(bucket.list_blobs(prefix=gcs_folder_path))
    os.makedirs(local_folder_path, exist_ok=True)

    tasks = []
    for blob in blobs:
        file_name = os.path.basename(blob.name)
        if file_name:
            local_file_path = os.path.join(local_folder_path, file_name)
            task = asyncio.get_running_loop().run_in_executor(
                executor, blob.download_to_filename, local_file_path
            )
            tasks.append(task)

    await asyncio.gather(*tasks)
    if not tasks:
        print(f"No files found in the specified GCS folder: {gcs_folder_path}")
    else:
        print("All files downloaded successfully.")


async def download_blob(blob, destination_file_name):
    """Download a blob from GCS asynchronously."""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, blob.download_to_filename, destination_file_name)
    except Exception as e:
        print(f"Error downloading {blob.name}: {e}")


async def download_blob(blob, destination_file_name):
    """Download a blob from GCS asynchronously."""
    # blob.download_to_filename는 블로킹 메서드이므로 asyncio.create_task()를 사용하여 비동기적으로 실행
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blob.download_to_filename, destination_file_name)

async def download_blobs(group_room_num):
    # Define the prefix based on the group room number
    prefix = f"rooms/{group_room_num}/"  # GCS에 저장된 경로에서 bucket 이름 제거

    # Get the current directory
    current_directory = os.getcwd()

    # Define the destination folders for downloading
    destination_folders = {
        "targets": os.path.join(current_directory, f"{group_room_num}/targets"),
        "image": os.path.join(current_directory, f"{group_room_num}/image"),
    }

    # Ensure the destination folders exist
    for folder in destination_folders.values():
        await ensure_directory_exists(folder)

    # List all blobs (files) in the bucket with the specified prefix
    blobs = await bucket.list_blobs(prefix=prefix)

    # Download each blob to the local destination folder, maintaining the structure
    async for blob in blobs:
        await print(f"when download_blobs, blob: {blob.name}")

        # Check if the blob is in the target or image folder
        if "targets/" in blob.name:
            destination_folder = destination_folders["targets"]
        elif "image/" in blob.name:
            destination_folder = destination_folders["image"]
        else:
            continue  # Skip if not in targets or image

        # Construct the relative path for the local file
        relative_path = blob.name[len(prefix):]  # Get the relative path
        local_file_path = os.path.join(destination_folder, relative_path)

        # Ensure the directory structure exists for the local file path
        local_file_dir = os.path.dirname(local_file_path)
        await ensure_directory_exists(local_file_dir)

        # Download the blob to the local file
        await print(f"Downloading {blob.name} to {local_file_path}...")
        await download_blob(blob, local_file_path)  # 비동기 다운로드

    await print("Download completed.")