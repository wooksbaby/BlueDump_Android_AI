from fastapi import FastAPI
from google.cloud import storage
import os

app = FastAPI()

# Google Cloud Storage에서 폴더의 모든 파일을 다운로드하는 함수
def download_folder_from_gcs(bucket_name, gcs_folder_path, local_folder_path):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # GCS에서 해당 경로의 모든 파일을 가져옴
    blobs = bucket.list_blobs(prefix=gcs_folder_path)
    os.makedirs(local_folder_path, exist_ok=True)

    for blob in blobs:
        # GCS 경로에서 파일 이름 추출
        file_name = os.path.basename(blob.name)
        local_file_path = os.path.join(local_folder_path, file_name)
        
        # 파일 다운로드
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {file_name} to {local_file_path}")

# FastAPI 엔드포인트 정의
@app.post("/process-folder/")
async def process_folder(gcs_folder_path: str):
    bucket_name = "your-gcs-bucket-name"
    local_folder_path = f"./temp/{gcs_folder_path}"

    # GCS 폴더 다운로드
    download_folder_from_gcs(bucket_name, gcs_folder_path, local_folder_path)

    # 로컬 폴더에서 다운로드 완료 후 이미지 처리 로직 추가 가능
    return {"message": f"Downloaded all images from {gcs_folder_path}"}
