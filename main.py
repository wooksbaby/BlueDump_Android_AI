from utils import classify_images_with_options
import os

if __name__ == "__main__":
    # 작업 디렉토리 설정
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, "target")
    images_directory = os.path.join(current_directory, "images")
    output_directory = os.path.join(current_directory, "classified_images_gcp")

    # JSON 키 파일 경로 설정
    credentials_path = '/home/wooksbaby/my_pri/gb-24-idv-108-5772e2cad8b5.json'

    # 사용 예시
    classify_images_with_options(target_directory, images_directory, output_directory, batch_size=128, credentials_path=credentials_path)
