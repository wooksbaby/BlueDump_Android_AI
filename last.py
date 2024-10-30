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
    try:
        if not image_path.endswith('.jpg'):
            jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
            with Image.open(image_path) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(jpg_path, 'JPEG')
            return jpg_path
        return image_path
    except Exception as e:
        print(f"Skipping file {image_path}: {e}")
        return None

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
    #target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    #images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]
    # convert_to_jpg 함수에서 None이 반환된 파일은 무시하도록 classify_images_with_options 함수에서 필터링을 추가
    target_images = [
        img for img in (convert_to_jpg(os.path.join(target_directory, f)) 
        for f in os.listdir(target_directory) if f.lower().endswith(('.jpg', '.jpeg', '.png')))
        if img is not None
    ]
    images = [
        img for img in (convert_to_jpg(os.path.join(images_directory, f)) 
        for f in os.listdir(images_directory) if f.lower().endswith(('.jpg', '.jpeg', '.png')))
        if img is not None
    ]

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

        # 각 옵션에 따라 결과가 저장될 디렉토리 설정
        option_directory = os.path.join(output_base_directory, f"{model_name}_{distance_metric}_{detector_backend}_align_{align}")
        ensure_directory_exists(option_directory)
        
        for image in images:
            for target_image in target_images:
                person_name = os.path.splitext(os.path.basename(target_image))[0]
                person_directory = os.path.join(option_directory, person_name)  # 각 옵션별 디렉토리 생성
                ensure_directory_exists(person_directory)

                try:
                    # DeepFace의 analyze 함수를 사용하여 얼굴 위치 감지
                    analysis = DeepFace.analyze(img_path=image, actions=['emotion'], detector_backend=detector_backend[0])
                    if len(analysis) == 0:
                        print(f"{os.path.basename(image)}에서 얼굴이 감지되지 않았습니다.")
                        continue

                    # 이미지에서 감지된 각 얼굴을 타겟과 비교
                    matched_regions = []
                    regions = [face['region'] for face in analysis if 'region' in face]
                    for idx, face in enumerate(analysis):
                        if 'region' in face:
                            region = face['region']
                            # 얼굴 영역 잘라내기
                            img = Image.open(image)
                            cropped_face = img.crop((region['x'], region['y'], region['x'] + region['w'], region['y'] + region['h']))
                            cropped_face_path = os.path.join(person_directory, f"{os.path.basename(image).rsplit('.', 1)[0]}_face_{idx}.jpg")
                            cropped_face.save(cropped_face_path)

                            # 잘라낸 얼굴과 타겟 이미지 비교
                            result = DeepFace.verify(
                                img1_path=target_image,
                                img2_path=cropped_face_path,
                                model_name=model_name[0],
                                distance_metric=distance_metric[0],
                                detector_backend=detector_backend[0],
                                enforce_detection=False,
                                align=align
                            )
                            if result["verified"]:
                                matched_regions.append(region)

                            # 잘라낸 얼굴 이미지 삭제
                            if os.path.exists(cropped_face_path):
                                os.remove(cropped_face_path)

                    # 매칭된 얼굴이 있는 경우 해당 인물별 폴더에 이미지 복사
                    if matched_regions:
                        shutil.copy(image, person_directory)
                        matched_count += 1  # 매칭된 이미지 수 증가
                        # 매칭된 경우의 유사도를 저장 (최초 매칭된 얼굴의 거리 사용)
                        similarities.append(result.get('distance', 0))
                        print(f"{person_name}의 이미지가 {os.path.basename(image)}에 {model_name}, {distance_metric}, {detector_backend}, align={align} 옵션으로 있습니다.")
                    else:
                        print(f"No matching faces found in {image}, skipping saving.")

                except Exception as e:
                    print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

        end_time = time.time()  # 종료 시간
        time_taken = end_time - start_time  # 소요 시간 계산
        log_time(model_name, distance_metric, detector_backend, align, matched_count, time_taken, similarities)  # 로그 기록

# 작업 디렉토리 설정
current_directory = os.getcwd()
target_directory = os.path.join(current_directory, "target")
images_directory = os.path.join(current_directory, "images")
output_directory = os.path.join(current_directory, "classified_images_new")  # 분류된 이미지를 저장할 외부 폴더

classify_images_with_options(target_directory, images_directory, output_directory)

