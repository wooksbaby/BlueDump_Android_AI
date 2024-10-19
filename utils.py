import os
import shutil
import time
from image_processing import convert_to_jpg, ensure_directory_exists, initialize_log_file
from face_detection import FaceDetector

def process_images_in_batches(target_images, images, batch_size, option_directory, detector):
    """주어진 배치 크기로 이미지를 처리하여 얼굴 탐지 및 복사"""
    image_count = 0

    for i in range(0, len(images), batch_size):
        batch_images = images[i:i + batch_size]

        for image in batch_images:
            for target_image in target_images:
                person_name = os.path.splitext(os.path.basename(target_image))[0]
                person_directory = os.path.join(option_directory, person_name)
                ensure_directory_exists(person_directory)

                try:
                    target_faces = detector.detect_faces(target_image)
                    source_faces = detector.detect_faces(image)

                    if target_faces and len(target_faces) == 1 and source_faces:
                        similar_faces = detector.compare_faces(target_faces[0], source_faces)

                        if similar_faces:
                            shutil.copy(image, person_directory)
                            image_count += 1
                            print(f"{person_name}의 이미지가 {os.path.basename(image)}에 있습니다.")
                        else:
                            print(f"{person_name}의 {os.path.basename(image)}에서 유사한 얼굴을 찾지 못했습니다.")
                    else:
                        print(f"{person_name}의 {os.path.basename(image)}에서 얼굴을 찾지 못했습니다.")
                except Exception as e:
                    print(f"{os.path.basename(image)}에서 얼굴을 찾을 수 없습니다: {e}")

    return image_count

def classify_images_with_options(target_directory, images_directory, output_base_directory, batch_size=1, credentials_path=''):
    """타겟 이미지를 기준으로 다양한 옵션으로 이미지 분류 및 저장"""
    log_file_path = os.path.join(output_base_directory, "log.txt")
    initialize_log_file(log_file_path)

    detector = FaceDetector(credentials_path)

    target_images = [convert_to_jpg(os.path.join(target_directory, f)) for f in os.listdir(target_directory)]
    images = [convert_to_jpg(os.path.join(images_directory, f)) for f in os.listdir(images_directory)]

    option_directory = os.path.join(output_base_directory, "Google_Vision_Face_Recognition")
    ensure_directory_exists(option_directory)

    start_time = time.time()
    image_count = process_images_in_batches(target_images, images, batch_size, option_directory, detector)

    elapsed_time = time.time() - start_time
    print(f"{option_directory}에 저장된 이미지 수: {image_count}, 처리 시간: {elapsed_time:.2f}초")

    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Google Cloud Vision, {image_count}, {elapsed_time:.2f}\n")

    target_image_count = sum(os.path.isdir(os.path.join(option_directory, name)) for name in os.listdir(option_directory))
    print(f"타겟 폴더의 이미지 수: {target_image_count}")
