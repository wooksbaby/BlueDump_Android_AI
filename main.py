from fastapi import FastAPI, BackgroundTasks
import os
from google.cloud import storage
import image_processing
from dotenv import load_dotenv
import shutil
from pydantic import BaseModel

# FastAPI 인스턴스 생성
app = FastAPI()


# .env 파일 로드
# .env 파일 로드
dotenv_path = "/home/BlueDump/.env"
load_dotenv(dotenv_path)

# 환경 변수 로드
bucket_name = os.getenv("GCS_BUCKET_NAME")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


# 로드된 환경 변수 확인
if bucket_name is None:
    print("GCS_BUCKET_NAME 환경 변수가 설정되지 않았습니다.")
else:
    print(f"Bucket Name: {bucket_name}")

if credentials_path is None:
    print("GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다.")
else:
    print(f"Credentials Path: {credentials_path}")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Google Cloud Storage 클라이언트 초기화
storage_client = storage.Client()

bucket = storage_client.bucket(bucket_name)

# Google Cloud Storage에 파일을 업로드하는 함수
def upload_folder_to_gcs(bucket, local_folder_path, destination_blob_prefix):
    for root, dirs, files in os.walk(local_folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            gcs_blob_path = os.path.join(destination_blob_prefix, relative_path)
            blob = bucket.blob(gcs_blob_path)
            blob.upload_from_filename(local_file_path)
            print(f"Uploaded {local_file_path} to {gcs_blob_path}")

# Google Cloud Storage에서 폴더의 모든 파일을 다운로드하는 함수
def download_folder_from_gcs(bucket, gcs_folder_path, local_folder_path):
    blobs = bucket.list_blobs(prefix=gcs_folder_path)
    os.makedirs(local_folder_path, exist_ok=True)
    found_files = False
    for blob in blobs:
        print(f"Found file: {blob.name}")
        found_files = True
        file_name = os.path.basename(blob.name)
        if file_name:
            local_file_path = os.path.join(local_folder_path, file_name)
            blob.download_to_filename(local_file_path)
            print(f"Downloaded {file_name} to {local_file_path}")
    if not found_files:
        print("No files found in the specified GCS folder.")

# POST 요청 처리
class Message(BaseModel):
    groupID: str  # groupID를 문자열로 받음

@app.post("/bluedump/")
async def send_message(msg: Message, background_tasks: BackgroundTasks):
    # temp 폴더 경로 설정
    temp_folder_path = "./temp"

    # temp 폴더가 존재하는지 확인
    if os.path.exists(temp_folder_path):
        shutil.rmtree(temp_folder_path)
        print(f"{temp_folder_path}가 삭제되었습니다.")
    else:
        print(f"{temp_folder_path} 폴더가 존재하지 않습니다.")

    global group_id
    group_id = msg.groupID  # groupID를 전역 변수로 설정
    background_tasks.add_task(handle_background_tasks)
    return {"message": f"You sent groupID: {group_id}"}

def handle_background_tasks():
    local_folder_path = "./temp/target"
    download_folder_from_gcs(bucket, f"rooms/{group_id}/targets/", local_folder_path)

    local_folder_path = "./temp/images"
    download_folder_from_gcs(bucket, f"rooms/{group_id}/image/", local_folder_path)

    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, "temp/target")
    images_directory = os.path.join(current_directory, "temp/images")
    output_directory = os.path.join(current_directory, "temp/return")

    image_processing.classify_images_with_options(target_directory, images_directory, output_directory)

    local_folder_path = "/home/BlueDump/BlueDump_Android_AI/temp/return"
    destination_blob_prefix = f"rooms/{group_id}/returns"
    upload_folder_to_gcs(bucket, local_folder_path, destination_blob_prefix)
    print("Finish!")


    #!!!!!!!!!!!!!!!!!마지막으로 자바서버에 완료했다고 리퀘스트 코드 추가하기!!!!!
    return
# 여기서 FastAPI 서버를 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
