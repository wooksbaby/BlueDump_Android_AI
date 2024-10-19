from google.cloud import vision
from google.oauth2 import service_account

class FaceDetector:
    def __init__(self, credentials_path):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self.client = vision.ImageAnnotatorClient(credentials=self.credentials)

    def detect_faces(self, image_path):
        """주어진 이미지 파일에서 얼굴을 탐지"""
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = self.client.face_detection(image=image)

        if response.error.message:
            raise Exception(f"{response.error.message}")

        return response.face_annotations

    def compare_faces(self, target_face, source_faces, distance_threshold=50):
        """타겟 얼굴과 소스 얼굴 간의 유사성을 비교하는 함수"""
        target_bbox = (target_face.bounding_poly.vertices[0].x, target_face.bounding_poly.vertices[0].y,
                       target_face.bounding_poly.vertices[2].x, target_face.bounding_poly.vertices[2].y)

        similar_faces = []
        for source_face in source_faces:
            source_bbox = (source_face.bounding_poly.vertices[0].x, source_face.bounding_poly.vertices[0].y,
                           source_face.bounding_poly.vertices[2].x, source_face.bounding_poly.vertices[2].y)

            if abs(target_bbox[0] - source_bbox[0]) < distance_threshold and \
               abs(target_bbox[1] - source_bbox[1]) < distance_threshold:
                similar_faces.append(source_face)

        return similar_faces
