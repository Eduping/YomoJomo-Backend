from celery import Celery
from config import Config

# Celery 앱 설정
celery_app = Celery(
    "ocr_tasks",
    broker=Config.CELERY_BROKER_URL,  # Redis를 브로커로 사용
    backend=Config.CELERY_BROKER_URL,  # 작업 결과 저장을 위한 백엔드
    include=["util.ocr_utiles"]
)

# Celery 앱 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # 직렬화 및 역직렬화 형식
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60  # 30분
)
