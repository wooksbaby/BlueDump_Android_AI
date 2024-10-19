from deepface import DeepFace  # DeepFace 라이브러리 임포트
import os  # OS 관련 작업을 위한 모듈
import shutil  # 파일 복사 등의 작업을 위한 모듈
from PIL import Image  # 이미지 처리(Pillow 라이브러리)
import tensorflow as tf  # GPU 상태 확인을 위한 TensorFlow

def convert_to_jpg(image_path):
    """
    이미지를 JPG 형식으로 변환하는 함수
    입력된 이미지 파일이 JPG가 아닌 경우, JPG로 변환하여 저장
    """
    if not image_path.endswith('.jpg'):
        # 확장자를 제외한 파일 경로 생성
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        # 이미지 열기 및 RGB로 변환 후 저장
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(jpg_path, 'JPEG')
        return jpg_path  # 변환된 JPG 파일 경로 반환
    return image_path  # 이미 JPG 파일인 경우 기존 경로 반환

def ensure_directory_exists(directory):
    """
    폴더가 없으면 새로 생성하는 함수
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def classify_images(target_directory, images_directory):
    """
    대상 디렉토리의 이미지와 비교하여, 동일한 사람이 있는 이미지를 분류하는 함수
    타겟 이미지와 비교 이미지를 각각 JPG로 변환 후 DeepFace를 통해 비교 수행
    """
    # 타겟 디렉토리 내 모든 파일을 JPG로 변환
    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    # 비교할 이미지 디렉토리 내 모든 파일을 JPG로 변환
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    # 각 타겟 이미지에 대해 비교 이미지들과 얼굴 비교
    for image in images:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]  # 타겟 이미지의 이름 추출
            person_directory = os.path.join(target_directory, person_name)  # 해당 인물의 폴더 생성 경로
            ensure_directory_exists(person_directory)  # 해당 인물 폴더가 없으면 생성

            try:
                # DeepFace를 사용해 타겟 이미지와 비교 이미지 비교
                result = DeepFace.verify(
                    img1_path=target_image,  # 타겟 이미지 경로
                    img2_path=image,  # 비교할 이미지 경로
                    model_name="ArcFace",  # 모델 이름(ArcFace 사용)
                    distance_metric="cosine",  # 거리 계산 방식으로 코사인 거리 사용
                    detector_backend="mtcnn",  # 얼굴 검출 방식으로 MTCNN 사용
                    enforce_detection=True,  # 얼굴이 없을 경우 오류 발생 설정
                    align=True  # 얼굴 정렬 옵션 사용
                )
                if result["verified"]:  # 얼굴이 일치하면
                    shutil.copy(image, person_directory)  # 해당 인물 폴더에 이미지 복사
                    print(f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다.")
            except Exception as e:
                print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")  # 오류 처리

# 현재 작업 디렉토리 경로 확인
current_directory = os.getcwd()
print(current_directory)

# 타겟 이미지와 비교 이미지 디렉토리 설정
target_directory = os.path.join(current_directory, "target")
images_directory = os.path.join(current_directory, "images")

# 사용 예시 - 타겟 디렉토리와 이미지 디렉토리 내 이미지 분류 작업 수행
classify_images(target_directory, images_directory)

# 사용 가능한 GPU 확인
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
