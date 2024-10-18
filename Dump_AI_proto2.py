from deepface import DeepFace
import os
import shutil
from PIL import Image
import tensorflow as tf

# GPU 사용을 명시적으로 설정
physical_devices = tf.config.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

def convert_to_jpg(image_path):
    """이미지 파일을 JPG로 변환"""
    if not image_path.endswith('.jpg'):
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(jpg_path, 'JPEG')
        return jpg_path
    return image_path

def ensure_directory_exists(directory):
    """디렉토리가 존재하지 않으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def classify_images(target_directory, images_directory, output_directory):
    """타겟 이미지를 기준으로 이미지 분류 및 저장"""
    # 타겟 디렉토리와 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    # 타겟 이미지에 대해 비교하고, 맞는 이미지 분류
    for image in images:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]
            person_directory = os.path.join(output_directory, person_name)  # 폴더를 타겟 디렉토리 밖에 생성
            ensure_directory_exists(person_directory)

            try:
                # DeepFace로 얼굴 비교 (GPU 사용)
                result = DeepFace.verify(
                    img1_path=target_image,
                    img2_path=image,
                    model_name="ArcFace",  # GPU를 활용하는 ArcFace 모델 사용
                    distance_metric="cosine",
                    detector_backend="mtcnn",  # MTCNN으로 얼굴 감지
                    enforce_detection=True,
                    align=True
                )
                if result["verified"]:
                    shutil.copy(image, person_directory)  # 타겟 폴더 외부에 파일 복사
                    print(f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다.")
            except Exception as e:
                print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

# 작업 디렉토리 설정
current_directory = os.getcwd()
target_directory = os.path.join(current_directory, "target")
images_directory = os.path.join(current_directory, "images")
output_directory = os.path.join(current_directory, "classified_images")  # 분류된 이미지를 저장할 외부 폴더

# 사용 예시
classify_images(target_directory, images_directory, output_directory)

# GPU 확인
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
