# 1. 베이스 이미지 선택
FROM python:3.10-slim

# 2. 작업 디렉터리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4. 애플리케이션 코드 복사
COPY app /app/

