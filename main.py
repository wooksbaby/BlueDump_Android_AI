from fastapi import FastAPI, HTTPException, UploadFile, File
import requests
import shutil
import os

app = FastAPI()

# 저장 경로 설정
SAVE_DIR = "/home/wooksbaby/BlueDump_Android_AI/saved_images"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.post("/upload-image/")
async def upload_image(image_url: str):
    """
    이미지 URL을 받아서 서버에 이미지를 저장하는 API.
    :param image_url: 타겟 이미지의 GCP 주소
    """
    try:
        # 이미지 다운로드
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # 파일 이름 추출 및 저장
            image_name = os.path.basename(image_url)
            save_path = os.path.join(SAVE_DIR, image_name)

            with open(save_path, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            return {"message": f"Image successfully saved as {image_name}", "path": save_path}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
