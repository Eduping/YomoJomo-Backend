import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from uuid import uuid4
import os
import logging
from config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION,
        )
        self.bucket_name = Config.AWS_S3_BUCKET
        self.cloudfront_url = Config.CLOUDFRONT_URL

    def upload_file(self, file, file_name, folder=""):
        """
        S3에 파일을 업로드하고 CloudFront URL 반환.

        :param file: 업로드할 파일 객체
        :param file_name: 업로드할 파일 이름
        :param folder: S3 버킷 내의 폴더 경로 (예: 'student_records/')
        :return: CloudFront URL
        """
        try:
            # 유니크한 파일 이름 생성
            unique_file_name = f"{folder}/{uuid4()}-{file_name}" if folder else f"{uuid4()}-{file_name}"

            # 파일 업로드
            self.s3.upload_fileobj(
                file, self.bucket_name, unique_file_name
            )

            # URL 생성 (CloudFront 우선)
            if self.cloudfront_url:
                file_url = f"{self.cloudfront_url}/{unique_file_name}"
            else:
                # S3 URL 생성
                file_url = f"{self.bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{unique_file_name}"

            logger.info(f"File uploaded successfully: {file_url}")
            return file_url
        except (NoCredentialsError, ClientError) as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def delete_file(self, file_url):
        """
        S3에서 파일 삭제.

        :param file_url: 삭제할 파일의 URL
        :return: 삭제 성공 여부
        """
        try:
            # URL에서 파일 키 추출
            if self.cloudfront_url and file_url.startswith(self.cloudfront_url):
                file_key = file_url.replace(f"{self.cloudfront_url}/", "")
            else:
                file_key = file_url.split("/")[-1]

            # 파일 삭제
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"File deleted successfully: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise