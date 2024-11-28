from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from util.s3_utils import S3Service
from util.examples import common_examples, create_example_response
from schemas import create_response
from crud.student_record_crud import create_pdf_file, get_pdf_file, soft_delete_pdf_file
from fastapi import Query
from auth.oauth2 import get_current_user
from models import StudentRecord
from fastapi.encoders import jsonable_encoder

router = APIRouter()
s3_service = S3Service()

@router.post(
    "",
    responses={
        200: create_example_response("File uploaded successfully", common_examples["upload_success"]),
        400: create_example_response("Invalid file format", common_examples["error_400_invalid_format"]),
    },
)
def upload_pdf(
    file: UploadFile,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 파일 형식 검증
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    # S3에 파일 업로드
    try:
        file_url = s3_service.upload_file(file.file, file.filename)
        new_file = create_pdf_file(db, file.filename, file_url, user_id)
        return create_response(200, True, "File uploaded successfully", {"file_url": file_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "",
    responses={
        200: create_example_response("File deleted successfully", common_examples["delete_success"]),
        400: create_example_response("File already deleted", common_examples["error_400_file_deleted"]),
        404: create_example_response("File not found", common_examples["error_404_file_not_found"]),
    },
)
def delete_pdf(file_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # DB에서 파일 정보 가져오기
    student_record = get_pdf_file(db, file_id)
    if not student_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )
    if student_record.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File already deleted."
        )

    # # S3에서 파일 삭제
    # try:
    #     s3_service.delete_file(student_record.file_url)
    #     db.delete(student_record)
    #     db.commit()
    #     return {"success": True, "message": "File deleted successfully."}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    # 소프트 삭제: deleted_at 필드 업데이트
    soft_delete_pdf_file(db, student_record)

    return create_response(200, True, "File deleted successfully")

@router.get(
    "",
    responses={
        200: create_example_response(
            "Student records retrieved successfully", common_examples["student_records_success"]
        ),
        404: create_example_response("No records found", common_examples["error_404_no_records"]),
    },
)
def get_student_records(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    """
    생활기록부 목록을 페이지네이션과 함께 반환합니다.
    """
    offset = (page - 1) * size

    # 생활기록부 목록 조회
    records = (
        db.query(StudentRecord)
        .filter(StudentRecord.user_id == user_id, StudentRecord.deleted_at.is_(None))
        .order_by(StudentRecord.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No records found."
        )

    # 전체 개수 계산
    total_count = (
        db.query(StudentRecord)
        .filter(StudentRecord.user_id == user_id, StudentRecord.deleted_at.is_(None))
        .count()
    )

    # 데이터 변환
    data = [
        {
            "id": record.id,
            "file_name": record.file_name,
            "file_url": record.file_url,
            "created_at": record.created_at,
        }
        for record in records
    ]

    return create_response(
        200,
        True,
        "Student records retrieved successfully",
        {
            "items": jsonable_encoder(data),
            "total": total_count,
            "page": page,
            "size": size,
        },
    )