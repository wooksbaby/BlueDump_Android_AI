import cv2  # OpenCV 라이브러리 추가

def draw_faces_on_image(image_path, faces, output_path):
    """탐지된 얼굴을 이미지에 표시하고 저장"""
    image = cv2.imread(image_path)  # 이미지 읽기

    # 각 얼굴에 대해 경계 상자를 그림
    for face in faces:
        vertices = face.bounding_poly.vertices
        x1 = vertices[0].x
        y1 = vertices[0].y
        x2 = vertices[2].x
        y2 = vertices[2].y
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 초록색 사각형 그리기

    cv2.imwrite(output_path, image)  # 이미지 저장
    print(f"얼굴 탐지 결과를 {output_path}에 저장했습니다.")

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

                    # 얼굴을 이미지에 표시하고 저장
                    output_image_path = os.path.join(person_directory, f"detected_faces_{os.path.basename(image)}")
                    draw_faces_on_image(image, source_faces, output_image_path)  # 탐지된 얼굴을 이미지에 표시

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
