from deepface import DeepFace
import os
import shutil
from PIL import Image
import tensorflow as tf

# GPU 사용을 명시적으로 설정
physical_devices = tf.config.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

# JPG로 이미지 변환 함수
def convert_to_jpg(image_path):
    """이미지 파일을 JPG로 변환"""
    if not image_path.endswith('.jpg'):
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(jpg_path, 'JPEG')
        return jpg_path
    return image_path

# 디렉토리 생성 함수
def ensure_directory_exists(directory):
    """디렉토리가 존재하지 않으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)

# 다양한 옵션으로 이미지 분류
def classify_images_with_options(target_directory, images_directory, output_base_directory):
    """타겟 이미지를 기준으로 다양한 옵션으로 이미지 분류 및 저장"""
    # 타겟 및 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    # 추가할 옵션 리스트들 (모델명, 거리 측정 방식, 얼굴 감지기, 정렬 여부)
    model_names = ["ArcFace", "VGG-Face", "Facenet", "OpenFace", "DeepFace"]
    distance_metrics = ["cosine", "euclidean", "euclidean_l2", "manhattan"]
    detector_backends = ["mtcnn", "ssd", "retinaface", "opencv"]
    align_options = [True, False]

    # 각 옵션 조합을 위한 다중 for문
    for model_name in model_names:
        for distance_metric in distance_metrics:
            for detector_backend in detector_backends:
                for align in align_options:
                    # 각 옵션에 따라 결과가 저장될 디렉토리 설정
                    option_directory = os.path.join(output_base_directory, f"{model_name}_{distance_metric}_{detector_backend}_align_{align}")
                    ensure_directory_exists(option_directory)

                    for image in images:
                        for target_image in target_images:
                            person_name = os.path.splitext(os.path.basename(target_image))[0]
                            person_directory = os.path.join(option_directory, person_name)  # 각 옵션별 디렉토리 생성
                            ensure_directory_exists(person_directory)

                            try:
                                # DeepFace로 얼굴 비교 (GPU 사용)
                                result = DeepFace.verify(
                                    img1_path=target_image,
                                    img2_path=image,
                                    model_name=model_name,
                                    distance_metric=distance_metric,
                                    detector_backend=detector_backend,
                                    enforce_detection=True,
                                    align=align
                                )
                                if result["verified"]:
                                    shutil.copy(image, person_directory)  # 타겟 폴더 외부에 파일 복사
                                    print(f"{person_name}의 이미지가 {os.path.basename(image)}에 {model_name}, {distance_metric}, {detector_backend}, align={align} 옵션으로 있습니다.")
                            except Exception as e:
                                print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

# 작업 디렉토리 설정
current_directory = os.getcwd()
target_directory = os.path.join(current_directory, "target")
images_directory = os.path.join(current_directory, "images")
output_directory = os.path.join(current_directory, "classified_images")  # 분류된 이미지를 저장할 외부 폴더

# 사용 예시
classify_images_with_options(target_directory, images_directory, output_directory)

# GPU 확인
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
