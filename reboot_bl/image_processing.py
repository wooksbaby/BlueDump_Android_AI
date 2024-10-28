import os
import shutil
from deepface import DeepFace
from utils import convert_to_jpg

async def ensure_directory_exists(directory):
    """디렉토리가 존재하지 않으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)

async def classify_images(target_directory, images_directory, output_base_directory):
    """타겟 이미지를 기준으로 이미지 분류 및 저장"""
    # Ensure the output base directory exists
    ensure_directory_exists(output_base_directory)

    # 타겟 및 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [
        convert_to_jpg(os.path.join(target_directory, f))
        for f in os.listdir(target_directory)
    ]
    images = [
        convert_to_jpg(os.path.join(images_directory, f))
        for f in os.listdir(images_directory)
    ]


    for image in images:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]
            person_directory = os.path.join(output_base_directory, person_name)  # 각 옵션별 디렉토리 생성
            
            # Ensure the person directory exists
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
                    print(f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다.")
            except Exception as e:
                print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")
