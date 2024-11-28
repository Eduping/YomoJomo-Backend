from sqlalchemy.orm import Session
from sqlalchemy import func
from models import StudentRecord
from typing import Optional

def create_pdf_file(db: Session, file_name: str, file_url: str, user_id: int) -> StudentRecord:
    """
    PDF 파일 정보를 생성하고 DB에 저장.
    """
    new_file = StudentRecord(file_name=file_name, file_url=file_url, user_id=user_id)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_pdf_file(db: Session, file_id: int) -> Optional[StudentRecord]:
    """
    PDF 파일 정보를 ID로 조회.
    """
    return db.query(StudentRecord).filter(StudentRecord.id == file_id).first()

def soft_delete_pdf_file(db: Session, pdf_file: StudentRecord):
    """
    PDF 파일을 소프트 삭제.
    """
    pdf_file.deleted_at = func.now()
    db.commit()