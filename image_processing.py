from deepface import DeepFace
import os
import shutil
import time
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

# 로그 기록 함수
def log_time(model_name, distance_metric, detector_backend, align, matched_count, time_taken, similarities):
    """로그 파일에 옵션, 매칭된 이미지 수, 걸린 시간, 유사도 점수 기록"""
    # 유사도 점수의 평균 계산
    average_similarity = sum(similarities) / len(similarities) if similarities else 0

    log_message = (
        f"모델: {model_name}, 거리 측정: {distance_metric}, 백엔드: {detector_backend}, align: {align}, "
        f"매칭된 이미지 수: {matched_count}, 걸린 시간: {time_taken:.2f}초\n"
        f"유사도 점수 평균: {average_similarity:.2f}\n"  # 평균 추가
    )
    
    with open("classification_log.txt", "a") as log_file:
        log_file.write(log_message)


# 다양한 옵션으로 이미지 분류
def classify_images_with_options(target_directory, images_directory, output_base_directory):
    """타겟 이미지를 기준으로 다양한 옵션으로 이미지 분류 및 저장"""
    # 타겟 및 이미지 디렉토리의 모든 파일을 JPG로 변환
    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    # 추가할 옵션 리스트들 (모델명, 거리 측정 방식, 얼굴 감지기, 정렬 여부)
    model_name = ["Facenet"]
    distance_metric = ["euclidean"]
    detector_backend = ["retinaface"]
    align_options = [True]

    # 각 옵션 조합을 위한 다중 for문
    for align in align_options:
        start_time = time.time()  # 시작 시간
        matched_count = 0  # 매칭된 이미지 수 초기화
        similarities = []  # 유사도 점수 리스트 초기화

                    # 결과가 저장될 디렉토리 설정
                    option_directory = os.path.join(output_base_directory)
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
                        matched_count += 1  # 매칭된 이미지 수 증가
                        similarities.append(result['distance'])  # 유사도 점수 저장
                        print(f"{person_name}의 이미지가 {os.path.basename(image)}에 {model_name}, {distance_metric}, {detector_backend}, align={align} 옵션으로 있습니다.")
                except Exception as e:
                    print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

        end_time = time.time()  # 종료 시간
        time_taken = end_time - start_time  # 소요 시간 계산
        log_time(model_name, distance_metric, detector_backend, align, matched_count, time_taken, similarities)  # 로그 기록

# 작업 디렉토리 설정

