import os

# 이미지가 저장된 최상위 경로 (classified_images 경로)
base_path = "/home/wooksbaby/BlueDump_Android_AI/classified_images"

# 문서화할 결과를 저장할 리스트
result = []

# base_path 하위의 폴더들을 순회
for model_name in os.listdir(base_path):
    model_path = os.path.join(base_path, model_name)
    
    # 모델 폴더 안에 있는 각 타겟 폴더를 순회
    if os.path.isdir(model_path):
        for target_name in os.listdir(model_path):
            target_path = os.path.join(model_path, target_name)
            
            # 타겟 폴더가 실제 디렉토리인지 확인
            if os.path.isdir(target_path):
                # 해당 타겟 폴더 내의 이미지 파일 목록을 가져오기 (이미지 파일 확장자에 따라 필터링 가능)
                image_files = [f for f in os.listdir(target_path) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                image_count = len(image_files)
                
                # 결과 저장
                result.append(f"Model: {model_name}, Target: {target_name}, Image Count: {image_count}")

# 결과를 문서로 출력 (파일로 저장 가능)
output_file = "/home/wooksbaby/BlueDump_Android_AI/image_count_report0237.txt"
with open(output_file, 'w') as f:
    for line in result:
        f.write(line + '\n')

print(f"이미지 수를 문서화한 결과가 {output_file}에 저장되었습니다.")
