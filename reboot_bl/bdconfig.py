import os
from dotenv import load_dotenv
from google.cloud import storage

# .env 파일 로드

# 여러 .env 파일 경로 정의
env_paths = [
    "/home/BlueDump/.env",
    "/home/BlueDump/BlueDump_Android_AI/reboot_bl/.env",
]

# 각 .env 파일을 순차적으로 로드
for env_path in env_paths:
    if os.path.exists(env_path):  # 파일이 존재하는지 확인
        load_dotenv(env_path, override=False)  # 이미 설정된 변수는 덮어쓰지 않음

# 이후에 환경 변수를 사용할 수 있습니다.
db_host = os.getenv("DB_HOST")

# GCS 환경 변수 로드
bucket_name = os.getenv("GCS_BUCKET_NAME")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# gcs_folder_prefix = "rooms/"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path


# DB 주소 (Google Cloud SQL을 위한 MySQL 연결 문자열)
# DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@/{os.getenv('DB_NAME')}?unix_socket=/cloudsql/{os.getenv('DB_HOST')}"
# print(DATABASE_URL)
DATABASE_URL = "mysql+pymysql://bluedump-py:0738asdf@34.47.87.18:3306/REBOOTBDDB"
ASYNC_DATABASE_URL = "mysql+aiomysql://bluedump-py:0738asdf@34.47.87.18:3306/REBOOTBDDB"

# 전역 GCS Client 및 Bucket 설정
client = storage.Client()
bucket = client.bucket(bucket_name)


# 예외 처리: 환경 변수가 없을 경우 경고 메시지 출력
if not all([bucket_name, credentials_path, DATABASE_URL]):
    raise ValueError("환경 변수가 누락되었습니다.")
