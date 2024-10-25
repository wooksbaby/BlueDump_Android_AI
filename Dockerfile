# 베이스 이미지로 miniconda3 사용
FROM continuumio/miniconda3

# 작업 디렉토리 설정
WORKDIR /app

# 환경 파일 복사
COPY environment.yml .

# 환경 업데이트 (기존 환경이 있으면 업데이트)
RUN conda env update -f environment.yml --prune || true

# 현재 디렉토리의 모든 파일 복사
COPY . .

# 활성화할 환경을 설정 (blueenv로 수정)
SHELL ["conda", "run", "-n blueenv", "/bin/bash", "-c"]

# 컨테이너 시작 시 실행할 커맨드
CMD ["python", "your_script.py"] 
