import os
import shutil
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from deepface import DeepFace
from google.cloud import storage
from bdconfig import bucket  # GCS 전역 객체 가져오기
from utils import convert_to_jpg


def ensure_directory_exists(directory):
    """디렉토리가 존재하지 않으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_images_from_gcs(
    room_id: int, target_directory: str, images_directory: str
):
    """GCS에서 타겟 이미지와 일반 이미지를 다운로드"""
    target_blob_prefix = f"rooms/{room_id}/target/"
    images_blob_prefix = f"rooms/{room_id}/images/"

    # 타겟 이미지 다운로드
    download_folder_from_gcs(target_blob_prefix, target_directory)

    # 일반 이미지 다운로드
    download_folder_from_gcs(images_blob_prefix, images_directory)


def download_folder_from_gcs(gcs_folder_path, local_folder_path):
    """GCS 폴더에서 로컬 폴더로 모든 파일 다운로드"""
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


def classify_images(target_directory, images_directory, output_base_directory):
    """타겟 이미지를 기준으로 이미지 분류 및 저장"""
    # 타겟 및 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [
        convert_to_jpg(os.path.join(target_directory, f))
        for f in os.listdir(target_directory)
    ]
    images = [
        convert_to_jpg(os.path.join(images_directory, f))
        for f in os.listdir(images_directory)
    ]

    matched_count = 0  # 매칭된 이미지 수 초기화
    similarities = []  # 유사도 점수 리스트 초기화

    # 결과가 저장될 디렉토리 설정
    option_directory = os.path.join(output_base_directory)
    ensure_directory_exists(option_directory)

    for image in images:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]
            person_directory = os.path.join(
                option_directory, person_name
            )  # 각 옵션별 디렉토리 생성
            ensure_directory_exists(person_directory)

            try:
                # DeepFace로 얼굴 비교
                result = DeepFace.verify(
                    img1_path=target_image,
                    img2_path=image,
                    model_name="Facenet",
                    distance_metric="euclidean",
                    detector_backend="retinaface",
                    enforce_detection=True,
                    align=True,
                )
                if result["verified"]:
                    shutil.copy(image, person_directory)  # 타겟 폴더 외부에 파일 복사
                    matched_count += 1  # 매칭된 이미지 수 증가
                    similarities.append(result["distance"])  # 유사도 점수 저장
                    print(
                        f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다."
                    )
            except Exception as e:
                print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")
