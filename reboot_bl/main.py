from fastapi import Request, FastAPI, HTTPException, Form, UploadFile, File
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routers import router
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os
import json
import tensorflow as tf

# Load environment variables from the .env file



load_dotenv("/home/BlueDump/.env")


# TensorFlow GPU 설정
physical_devices = tf.config.list_physical_devices("GPU")
if physical_devices:
    for gpu in physical_devices:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("No GPU found.")

app = FastAPI(debug=True)

# CORS Middleware configuration (optional, based on your requirements)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers
app.include_router(router, prefix="/api")  # Add a prefix if needed


# Lifespan event handler
@app.on_event("startup")
async def startup_event():
    print("Starting up...")  # Code to run at startup


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")  # Code to run at shutdown


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": str(request.url)},
    )


@app.post("/submit/")
async def submit_form(name: str = Form(...), age: int = Form(...)):
    return {"name": name, "age": age}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error_msg": "Validation error occurred.",
            "error_type": "ValidationError",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"success": False, "detail": exc.detail}
    )


# URL 경로에 대한 라우터 정의
@app.get("/")
async def root():
    return {"message": "Welcome to the Group Room API"}



@app.get("/.well-known/invitePage.html", response_class=HTMLResponse)
async def serve_invite_page():
    file_path = "/home/BlueDump/.well-known/invitePage.html"
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="파일을 찾을 수 없습니다.", status_code=404)

@app.get("/.well-known/assetlinks.json", response_class=JSONResponse)
async def serve_assetlinks():
    file_path = "/home/BlueDump/.well-known/assetlinks.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = json.load(file)
        return JSONResponse(content=content)
    else:
        return JSONResponse(content={"error": "파일을 찾을 수 없습니다."}, status_code=404)



# Run the application using Uvicorn if this script is executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
