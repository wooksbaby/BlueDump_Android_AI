import os
from bdconfig import bucket  # 전역 객체 불러오기
from google.cloud import storage
from fastapi import UploadFile, HTTPException


# 환경 변수 설정
async def copy_profile_image_in_gcs(source_blob_name: str, destination_blob_name: str):
    """GCS에서 프로필 이미지를 복사하는 함수."""
    source_blob = bucket.blob(source_blob_name)

    # 이미지 복사
    try:
        # copy_blob 메서드를 사용하여 소스 블롭을 대상 블롭으로 복사
        bucket.copy_blob(source_blob, bucket, destination_blob_name)
        print(f"Copied {source_blob_name} to {destination_blob_name}")
    except Exception as e:
        # 복사 실패 시 HTTPException 발생
        raise HTTPException(
            status_code=500, detail=f"Failed to copy profile image: {str(e)}"
        )


async def upload_file_to_gcs(file: UploadFile, destination_blob_name: str) -> bool:
    try:
        blob = bucket.blob(destination_blob_name)

        # 파일을 GCS로 업로드
        blob.upload_from_file(file.file, content_type=file.content_type)

        return True
    except Exception as e:
        print(f"An error occurred while uploading to GCS: {e}")
        return False


async def upload_folder_to_gcs(local_folder_path, destination_blob_prefix):
    for root, _, files in os.walk(local_folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            gcs_blob_path = os.path.join(destination_blob_prefix, relative_path)
            blob = bucket.blob(gcs_blob_path)
            blob.upload_from_filename(local_file_path)
            print(f"Uploaded {local_file_path} to {gcs_blob_path}")


async def download_folder_from_gcs(gcs_folder_path, local_folder_path):
    """GCS 폴더에서 로컬 폴더로 모든 파일 다운로드"""
    blobs = bucket.list_blobs(prefix=gcs_folder_path)
    os.makedirs(local_folder_path, exist_ok=True)
    
    found_files = False

    for blob in blobs:
        found_files = True
        file_name = os.path.basename(blob.name)
        if file_name:
            local_file_path = os.path.join(local_folder_path, file_name)
            blob.download_to_filename(local_file_path)
            print(f"Downloaded {file_name} to {local_file_path}")

    if not found_files:
        print(f"No files found in the specified GCS folder: {gcs_folder_path}")


async def download_images_from_gcs(room_id , target_directory, images_directory):
    target_blob_prefix = f"targets/{room_id}/"
    images_blob_prefix = f"image/{room_id}/"

    # Download target images
    download_folder_from_gcs(target_blob_prefix, target_directory)

    # Download regular images
    download_folder_from_gcs(images_blob_prefix, images_directory)





    
async def download_folder_from_gcs(gcs_folder_path, local_folder_path):
    """GCS 폴더에서 로컬 폴더로 모든 파일 다운로드"""
    print(f"GCS folder path: {gcs_folder_path}")
    blobs = list(bucket.list_blobs(prefix=gcs_folder_path))  # Convert iterator to a list
    print(f"Blobs in {gcs_folder_path}: {blobs}")
    print(f"Local folder path: {local_folder_path}")

    os.makedirs(local_folder_path, exist_ok=True)
    found_files = False

    print(f"Found files in {gcs_folder_path}:")
    for blob in blobs:
        print(f"Found file: {blob.name}")
        found_files = True
        file_name = os.path.basename(blob.name)
        if file_name:  # Ensure file_name is not empty
            local_file_path = os.path.join(local_folder_path, file_name)
            blob.download_to_filename(local_file_path)
            print(f"Downloaded {file_name} to {local_file_path}")

    if not found_files:
        print("No files found in the specified GCS folder.")



async def download_blobs(group_room_num):
    # Define the prefix based on the group room number
    prefix = f'cloud-bucket-bluedump/rooms/{group_room_num}/'
    # Define the destination folder to keep the same structure as GCS
    # Get the current working directory
    current_directory = os.getcwd()
    destination_folder = os.path.join(current_directory, prefix)  # Combine current directory with the prefix

    # List all blobs (files) in the bucket with the specified prefix
    blobs = bucket.list_blobs(prefix=prefix)

    # Download each blob to the local destination folder
    for blob in blobs:
        # Construct the full local path
        local_file_path = os.path.join(destination_folder, blob.name[len(prefix):])

        # Create subdirectories if necessary
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the blob to the local file
        print(f'Downloading {blob.name} to {local_file_path}...')
        blob.download_to_filename(local_file_path)

    print('Download completed.')
