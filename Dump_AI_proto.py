from deepface import DeepFace
import os
import shutil
from PIL import Image
import tensorflow as tf

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

def convert_to_jpg(image_path):
    # 이미지 파일을 JPG로 변환
    if not image_path.endswith('.jpg'):
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(jpg_path, 'JPEG')
        return jpg_path
    return image_path

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def classify_images(target_directory, images_directory):
    # 타겟 디렉토리와 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    # 각 타겟 이미지에 대해 이미지 디렉토리의 모든 이미지와 비교
    for image in images:
        for target_image in target_images:
            person_name = os.path.splitext(os.path.basename(target_image))[0]
            person_directory = os.path.join(target_directory, person_name)
            ensure_directory_exists(person_directory)

            try:
                result = DeepFace.verify(
                    img1_path=target_image,
                    img2_path=image,
                    model_name="ArcFace",
                    distance_metric="cosine",
                    detector_backend="mtcnn",
                    enforce_detection=True,
                    align=True
                )
                if result["verified"]:
                    shutil.copy(image, person_directory)
                    print(f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다.")
            except Exception as e:
                print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

# 작업 디렉토리 설정
current_directory = os.getcwd()
target_directory = os.path.join(current_directory, "target")
images_directory = os.path.join(current_directory, "images")

# 사용 예시
classify_images(target_directory, images_directory)

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

