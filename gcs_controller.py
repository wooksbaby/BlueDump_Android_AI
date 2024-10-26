import os
from google.cloud import storage

# Google Cloud Storage 클라이언트 초기화
storage_client = storage.Client()
bucket_name = os.getenv("GCS_BUCKET_NAME")

if bucket_name is None:
    raise ValueError("GCS_BUCKET_NAME 환경 변수가 설정되지 않았습니다.")
bucket = storage_client.bucket(bucket_name)

# Google Cloud Storage에 파일을 업로드하는 함수
def upload_to_gcs(file, filename, destination_blob_prefix):
    blob = bucket.blob(f"{destination_blob_prefix}{filename}")
    blob.upload_from_file(file)  # file이 io.BufferedReader 타입인지 확인
    print(f"Uploaded {filename} to {destination_blob_prefix}")

# Google Cloud Storage에서 폴더의 모든 파일을 다운로드하는 함수
def download_from_gcs(gcs_folder_path, local_folder_path):
    blobs = bucket.list_blobs(prefix=gcs_folder_path)
    os.makedirs(local_folder_path, exist_ok=True)
    found_files = False
    for blob in blobs:
        print(f"Found file: {blob.name}")
        found_files = True
        file_name = os.path.basename(blob.name)
        if file_name:
            local_file_path = os.path.join(local_folder_path, file_name)
            try:
                blob.download_to_filename(local_file_path)
                print(f"Downloaded {file_name} to {local_file_path}")
            except Exception as e:
                print(f"Failed to download {file_name}: {str(e)}")
    if not found_files:
        print("No files found in the specified GCS folder.")

def upload_folder_to_gcs(local_folder_path, destination_blob_prefix):
    for root, dirs, files in os.walk(local_folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            blob = bucket.blob(f"{destination_blob_prefix}{file_name}")
            blob.upload_from_filename(local_file_path)
            print(f"Uploaded {file_name} to {destination_blob_prefix}")

def handle_background_tasks(group_id: str):
    local_folder_path = "./temp/target"
    download_from_gcs(f"rooms/{group_id}/targets/", local_folder_path)

    local_folder_path = "./temp/images"
    download_from_gcs(f"rooms/{group_id}/image/", local_folder_path)

    local_folder_path = "/home/BlueDump/BlueDump_Android_AI/temp/return"
    destination_blob_prefix = f"rooms/{group_id}/returns"
    upload_folder_to_gcs(local_folder_path, destination_blob_prefix)
    print("Finish!")
