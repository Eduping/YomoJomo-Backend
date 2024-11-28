from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from util.s3_utils import S3Service
from schemas import create_response
from crud.student_record_crud import create_pdf_file, get_pdf_file, soft_delete_pdf_file
router = APIRouter()
s3_service = S3Service()

@router.post("/upload")
def upload_pdf(
    user_id: int,
    file: UploadFile,
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

@router.delete("/delete", response_model=dict)
def delete_pdf(file_id: int, db: Session = Depends(get_db)):
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