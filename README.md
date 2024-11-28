# ChatBot API

ChatBot API는 사용자 인증, 채팅방 생성, 메시지 관리, PDF 파일 업로드 및 삭제 기능을 제공하는 FastAPI 기반의 웹 애플리케이션입니다. 이 문서에서는 프로젝트의 실행 방법과 주요 설정에 대해 설명합니다.


## 요구 사항 (Prerequisites)

* Python 3.10 이상
* Docker 및 Docker Compose
* AWS S3 및 CloudFront 설정 (PDF 파일 업로드를 위한 버킷 필요)
* .env 파일 생성 (환경 변수 설정)


## 설치 및 실행

### 1. 프로젝트 클론
```angular2html
git clone https://github.com/EduAI-Solutions/Eduping-Backend.git
cd Eduping-Backend
```

### 2. 가상 환경 설정 및 종속성 설치 (로컬 실행 시)

가상 환경 생성
```angular2html
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
종속성 설치
```angular2html
pip install -r requirements.txt
```
### 3. 환경 변수 파일 생성
.env 파일

프로젝트 루트 디렉토리에 .env 파일을 생성하고 아래 내용을 추가합니다.
```angular2html
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
DATABASE_HOST=

JWT_SECRET=
JWT_REFRESH_SECRET=
JWT_ALGORITHM=
ACCESS_TOKEN_EXPIRE_HOURS=
REFRESH_TOKEN_EXPIRE_DAYS=

LANGCHAIN_TRACING_V2=
LANGCHAIN_ENDPOINT=
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=p20241014
OPENAI_API_KEY=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_S3_BUCKET=
CLOUDFRONT_URL=
```
### 4. 데이터베이스 설정 및 마이그레이션

Docker Compose로 데이터베이스 실행
```angular2html
docker-compose up --build -d
```

Alembic 마이그레이션
```angular2html
alembic upgrade head
```