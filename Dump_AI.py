from deepface import DeepFace
import os
import shutil

def add_image_to_directory(image_path, images_directory):
    try:
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)
        shutil.copy(image_path, images_directory)
        print(f"{image_path}가 {images_directory}에 추가되었습니다.")
    except Exception as e:
        print(f"이미지를 추가하는 중 오류가 발생했습니다: {e}")

def find_person_in_images(target_image_path, images_directory):
    # 타겟 이미지의 얼굴 분석
    try:
        target_representation = DeepFace.represent(target_image_path, model_name="VGG-Face")
    except Exception as e:
        print(f"타겟 이미지에서 얼굴을 찾을 수 없습니다: {e}")
        return

    # 이미지 디렉토리에서 모든 파일을 순회
    for image_file in os.listdir(images_directory):
        image_path = os.path.join(images_directory, image_file)
        try:
            # 각 이미지의 얼굴 분석
            result = DeepFace.verify(img1_path=target_image_path, img2_path=image_path, model_name="VGG-Face")
            if result["verified"]:
                print(f"일치하는 얼굴을 찾았습니다: {image_file}")
        except Exception as e:
            print(f"{image_file}에서 얼굴을 찾을 수 없습니다: {e}")

# 작업 디렉토리 설정
current_directory = os.getcwd()
target_image_path = os.path.join(current_directory, "test2.png")
images_directory = os.path.join(current_directory, "images")

# 사용 예시
find_person_in_images(target_image_path, images_directory)
