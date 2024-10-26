from fastapi import Request, FastAPI, HTTPException, Form, UploadFile, File
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routers import router
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import List

# Load environment variables from the .env file
load_dotenv("/home/BlueDump/.env")

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
def submit_form(name: str = Form(...), age: int = Form(...)):
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


# 여기에 get_db와 GroupRoom 모델 정의도 포함해야 합니다.

app.include_router(router)


# Run the application using Uvicorn if this script is executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
