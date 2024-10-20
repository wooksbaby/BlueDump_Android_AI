from google.cloud import vision
import io
import os

def detect_faces(image_path):
    """Detects faces in an image file and returns face bounding boxes."""
    # 클라이언트 초기화
    client = vision.ImageAnnotatorClient()

    # 이미지 파일 열기
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    # 이미지 객체 생성
    image = vision.Image(content=content)

    # 얼굴 탐지 요청
    response = client.face_detection(image=image)
    faces = response.face_annotations

    # 응답 확인
    if response.error.message:
        raise Exception(f'{response.error.message}')

    # 탐지된 얼굴의 경계 상자 리스트 반환
    return [face.bounding_poly for face in faces]

def compare_faces(target_faces, detected_faces):
    """Compares target faces with detected faces."""
    # 여기서 유사도 비교 로직을 구현합니다.
    # 예를 들어, bounding box의 위치와 크기를 비교하는 방식으로 간단히 구현할 수 있습니다.
    # 이 예시에서는 단순히 리스트의 길이로 비교합니다.
    
    return len(target_faces) > 0 and len(detected_faces) > 0

def main(images_folder, target_folder):
    """Main function to detect faces in images and compare with targets."""
    # 모든 이미지 파일과 대상 얼굴 파일 가져오기
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpg', '.png'))]
    target_files = [f for f in os.listdir(target_folder) if f.endswith(('.jpg', '.png'))]

    # 각 타겟 얼굴의 경계 상자 수집
    target_faces = []
    for target_file in target_files:
        target_faces.append(detect_faces(os.path.join(target_folder, target_file)))

    # 각 이미지에서 얼굴 탐지 및 비교
    for image_file in image_files:
        detected_faces = detect_faces(os.path.join(images_folder, image_file))
        print(f'Detected faces in {image_file}: {len(detected_faces)}')

        for i, target_face in enumerate(target_faces):
            if compare_faces(target_face, detected_faces):
                print(f'Person in {target_file} detected in {image_file}!')

# 사용 예시
images_folder = 'images'  # 이미지 폴더 경로
target_folder = 'target_test'   # 타겟 폴더 경로
main(images_folder, target_folder)
