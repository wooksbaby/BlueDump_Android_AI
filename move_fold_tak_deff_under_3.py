import os
import shutil

# 원본 폴더 경로
source_root = "/home/wooksbaby/BlueDump_Android_AI/classified_images"
# 복사할 대상 폴더 경로
destination_root = "/home/wooksbaby/BlueDump_Android_AI/1over_under_3_images"

# 타겟 폴더 리스트 (각각의 모델 이름들)
target_folders = ['tak', 'deffcon']

# 각종모델명들 폴더 내의 모든 상위 폴더를 탐색
for model_folder in os.listdir(source_root):
    model_path = os.path.join(source_root, model_folder)
    
    # 상위 폴더가 존재하는지 확인
    if os.path.isdir(model_path):
        should_copy = False  # 상위 폴더를 복사할지 여부를 저장

        for target_folder in target_folders:
            folder_path = os.path.join(model_path, target_folder)
            
            # 타겟 폴더가 존재하고 디렉토리인지 확인
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # 이미지 파일 목록을 가져옴
                images = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                
                # 이미지가 1개 이상 3개 이하일 경우
                if 1 <= len(images) <= 3:
                    should_copy = True  # 상위 폴더를 복사할 조건 충족
                    print(f"{model_folder}/{target_folder} 폴더의 이미지가 {len(images)}개로 복사 대상입니다.")
                else:
                    print(f"{model_folder}/{target_folder} 폴더의 이미지가 {len(images)}개로 복사되지 않습니다.")

        # 상위 폴더를 복사할 조건이 충족된 경우
        if should_copy:
            destination_model_path = os.path.join(destination_root, model_folder)
            shutil.copytree(model_path, destination_model_path)  # 상위 폴더 전체 복사
            print(f"{model_folder} 폴더가 {destination_model_path}로 복사되었습니다.")
