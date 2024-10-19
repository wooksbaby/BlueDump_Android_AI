import os
import shutil

# 이미지 파일 확장자 목록
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

def count_images_in_directory(directory):
    """
    주어진 디렉토리 하위의 모든 이미지 파일을 세는 함수
    """
    image_count = 0
    # 디렉토리 하위의 모든 파일 및 하위 폴더를 순회
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 이미지 파일 확장자에 해당하면 카운트 증가
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_count += 1
    return image_count

def rename_folders_with_image_count(base_directory):
    """
    base_directory 하위의 각 폴더명을 이미지 파일 개수에 맞춰 변경하는 함수
    이미 처리된 폴더는 다시 처리하지 않음.
    """
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)
        if os.path.isdir(folder_path):  # 폴더인지 확인

            # 이미 폴더명이 '_숫자'로 끝난 경우 처리하지 않음
            if folder_name.rsplit('_', 1)[-1].isdigit():
                print(f"이미 처리된 폴더: {folder_name}, 건너뜁니다.")
                continue

            image_count = count_images_in_directory(folder_path)  # 해당 폴더 내 이미지 개수 계산
            new_folder_name = f"{folder_name}_{image_count}"  # 새 폴더명 (기존 이름 + 이미지 개수)
            new_folder_path = os.path.join(base_directory, new_folder_name)
            shutil.move(folder_path, new_folder_path)  # 폴더명 변경
            print(f"폴더명 변경: {folder_name} -> {new_folder_name}")

# 작업 디렉토리 설정
base_directory = "/home/wooksbaby/BlueDump_Android_AI/classified_images"

# 폴더명 변경 함수 호출
rename_folders_with_image_count(base_directory)
