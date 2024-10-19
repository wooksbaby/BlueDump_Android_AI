from google.cloud import vision
import os
import shutil
from PIL import Image
import time
from dotenv import load_dotenv
from google.oauth2 import service_account

# JSON 키 파일 경로 설정
credentials_path = '/home/wooksbaby/my_pri/gb-24-idv-108-5772e2cad8b5.json'

# Google Cloud 서비스 계정 자격 증명 생성
credentials = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]  # Google Cloud 플랫폼 접근 권한 부여
)

# Google Cloud Vision 클라이언트 생성
client = vision.ImageAnnotatorClient(credentials=credentials)

# JPG로 이미지 변환 함수 정의
def convert_to_jpg(image_path):
    """이미지 파일을 JPG 형식으로 변환"""
    if not image_path.endswith('.jpg'):  # 이미지 파일이 이미 JPG가 아닌 경우
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'  # 새 JPG 파일 경로 설정
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')  # 이미지를 RGB 모드로 변환
            rgb_img.save(jpg_path, 'JPEG')  # JPG 형식으로 저장
        return jpg_path  # 변환된 JPG 파일 경로 반환
    return image_path  # 이미 JPG인 경우 원래 경로 반환

# 디렉토리 생성 함수 정의
def ensure_directory_exists(directory):
    """주어진 디렉토리가 존재하지 않으면 생성"""
    if not os.path.exists(directory):  # 디렉토리가 없으면
        os.makedirs(directory)  # 새로 생성

# 로그 파일 초기화 함수 정의
def initialize_log_file(log_file_path):
    """로그 파일을 초기화하고 헤더를 작성"""
    ensure_directory_exists(os.path.dirname(log_file_path))  # 로그 파일 경로의 디렉토리가 없으면 생성
    with open(log_file_path, 'w') as log_file:
        log_file.write("모델명, 이미지 수, 처리 시간\n")  # 로그 파일 헤더 작성

# Google Cloud Vision API를 사용하여 얼굴 탐지 함수 정의
def detect_faces(image_path):
    """주어진 이미지 파일에서 얼굴을 탐지"""
    with open(image_path, 'rb') as image_file:
        content = image_file.read()  # 이미지 파일 내용을 읽기
    
    image = vision.Image(content=content)  # 이미지 객체 생성
    response = client.face_detection(image=image)  # 얼굴 탐지 요청

    if response.error.message:  # 오류가 발생한 경우
        raise Exception(f"{response.error.message}")  # 오류 메시지 출력
    
    return response.face_annotations  # 얼굴 주석 반환

# 이미지를 배치로 처리하는 함수 정의
def compare_faces(target_face, source_faces, distance_threshold=50):
    """타겟 얼굴과 소스 얼굴 간의 유사성을 비교하는 함수"""
    target_bbox = (target_face.bounding_poly.vertices[0].x, target_face.bounding_poly.vertices[0].y,
                   target_face.bounding_poly.vertices[2].x, target_face.bounding_poly.vertices[2].y)

    similar_faces = []
    for source_face in source_faces:
        source_bbox = (source_face.bounding_poly.vertices[0].x, source_face.bounding_poly.vertices[0].y,
                       source_face.bounding_poly.vertices[2].x, source_face.bounding_poly.vertices[2].y)

        # 거리 기준을 distance_threshold로 변경
        if abs(target_bbox[0] - source_bbox[0]) < distance_threshold and \
           abs(target_bbox[1] - source_bbox[1]) < distance_threshold:
            similar_faces.append(source_face)

    return similar_faces

def process_images_in_batches(target_images, images, batch_size, option_directory):
    """주어진 배치 크기로 이미지를 처리하여 얼굴 탐지 및 복사"""
    image_count = 0  # 복사된 이미지 수 초기화
    
    # 이미지 리스트를 배치 크기만큼 나누어 처리
    for i in range(0, len(images), batch_size):
        batch_images = images[i:i + batch_size]  # 현재 배치의 이미지 리스트
        
        # 배치 내의 각 이미지에 대해 반복
        for image in batch_images:
            # 각 타겟 이미지에 대해 반복
            for target_image in target_images:
                person_name = os.path.splitext(os.path.basename(target_image))[0]  # 타겟 이미지의 이름 추출
                person_directory = os.path.join(option_directory, person_name)  # 타겟 이미지에 대한 디렉토리 경로 설정
                ensure_directory_exists(person_directory)  # 해당 디렉토리가 없으면 생성

                try:
                    # 타겟 이미지와 현재 이미지에서 얼굴 탐지
                    target_faces = detect_faces(target_image)
                    source_faces = detect_faces(image)

                    # 타겟 얼굴이 하나일 경우
                    if target_faces and len(target_faces) == 1 and source_faces:
                        similar_faces = compare_faces(target_faces[0], source_faces)

                        if similar_faces:  # 유사한 얼굴이 발견된 경우
                            shutil.copy(image, person_directory)
                            image_count += 1  # 복사된 이미지 수 증가
                            print(f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다.")
                        else:
                            print(f"{person_name}의 {os.path.basename(image)}에서 유사한 얼굴을 찾지 못했습니다.")
                    else:
                        # 얼굴이 검출되지 않은 경우 메시지 출력
                        print(f"{person_name}의 {os.path.basename(image)}에서 얼굴을 찾지 못했습니다.")
                except Exception as e:
                    # 예외가 발생한 경우 오류 메시지 출력
                    print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

    return image_count  # 총 복사된 이미지 수 반환


# 다양한 옵션으로 이미지 분류 함수 정의
def classify_images_with_options(target_directory, images_directory, output_base_directory, batch_size=1):
    """타겟 이미지를 기준으로 다양한 옵션으로 이미지 분류 및 저장"""
    log_file_path = os.path.join(output_base_directory, "log.txt")  # 로그 파일 경로 설정
    initialize_log_file(log_file_path)  # 로그 파일 초기화

    # 타겟 이미지와 소스 이미지를 JPG로 변환하여 리스트 생성
    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    option_directory = os.path.join(output_base_directory, "Google_Vision_Face_Recognition")  # 결과 저장 경로 설정
    ensure_directory_exists(option_directory)  # 해당 디렉토리가 없으면 생성

    start_time = time.time()  # 처리 시작 시간 기록
    image_count = process_images_in_batches(target_images, images, batch_size, option_directory)  # 배치 처리 함수 호출

    elapsed_time = time.time() - start_time  # 처리 시간 계산
    print(f"{option_directory}에 저장된 이미지 수: {image_count}, 처리 시간: {elapsed_time:.2f}초")

    # 로그 파일에 처리 결과 기록
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Google Cloud Vision, {image_count}, {elapsed_time:.2f}\n")

    # 저장된 타겟 이미지 수 카운트
    target_image_count = sum(os.path.isdir(os.path.join(option_directory, name)) for name in os.listdir(option_directory))
    print(f"타겟 폴더의 이미지 수: {target_image_count}")

# 작업 디렉토리 설정
current_directory = os.getcwd()  # 현재 작업 디렉토리 가져오기
target_directory = os.path.join(current_directory, "target")  # 타겟 이미지 디렉토리 경로
images_directory = os.path.join(current_directory, "images")  # 소스 이미지 디렉토리 경로
output_directory = os.path.join(current_directory, "classified_images_gcp")  # 결과 저장 디렉토리 경로

# 사용 예시
classify_images_with_options(target_directory, images_directory, output_directory, batch_size=128)  # 이미지 분류 함수 호출
