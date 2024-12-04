from typing import Dict
from fastapi import HTTPException
import requests
import uuid
import time
import json
import re
from collections import defaultdict
from PyPDF2 import PdfReader, PdfWriter
from celery_config import celery_app
from config import Config
from util.s3_utils import S3Service
from crud.student_record_crud import create_pdf_file
import io
from database import get_db
from celery import chord


s3_service = S3Service()

@celery_app.task
def process_ocr_results(results, file_bytes, filename, user_id):
    """
    그룹 태스크 완료 후 결과를 처리하고 S3 업로드 및 DB 저장을 수행하는 태스크
    """
    # 결과 병합
    combined_text = "".join(results)
    ocr_data = parse_ocr_text(combined_text)

    # S3에 파일 업로드
    try:
        file_url = s3_service.upload_file(io.BytesIO(file_bytes), filename)
    except Exception as e:
        raise Exception(f"S3 업로드 실패: {str(e)}")

    # DB 저장
    try:
        db = next(get_db())  # get_db는 generator이므로 next로 호출
        create_pdf_file(db, filename, file_url, user_id, ocr_data)
    except Exception as e:
        raise Exception(f"DB 저장 실패: {str(e)}")

    return {"file_url": file_url, "ocr_data": ocr_data}


@celery_app.task(bind=True)
def split_and_ocr_pdf_with_celery(self, file_bytes: bytes, filename, user_id: int):
    """
    PDF 파일을 분할하고 OCR 작업을 비동기로 실행하는 태스크
    """
    max_pages = 10
    reader = PdfReader(io.BytesIO(file_bytes))
    total_pages = len(reader.pages)

    # 작업 상태 초기화
    self.update_state(state="STARTED", meta={"completed": 0, "total": total_pages})

    tasks = []
    num_files = (total_pages + max_pages - 1) // max_pages  # 필요한 파일 수 계산

    for i in range(num_files):
        writer = PdfWriter()
        start_page = i * max_pages
        end_page = min(start_page + max_pages, total_pages)

        for j in range(start_page, end_page):
            writer.add_page(reader.pages[j])

        # PDF 조각을 메모리로 저장
        pdf_buffer = io.BytesIO()
        writer.write(pdf_buffer)
        pdf_buffer.seek(0)

        # OCR 작업을 태스크로 생성
        tasks.append(ocr_pdf_from_memory.s(pdf_buffer.read(), f"split_{i + 1}.pdf"))

    # 작업 그룹을 생성하고 후속 태스크를 연결
    callback = process_ocr_results.s(file_bytes, filename, user_id)
    chord(tasks)(callback)

    return {
        "message": "OCR 작업",
        "total_pages": total_pages,
    }
@celery_app.task
def ocr_pdf_from_memory(pdf_bytes, file_name="split_part.pdf"):
    request_json = {
        "images": [
            {
                "format": "pdf",
                "name": file_name,
            }
        ],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(round(time.time() * 1000)),
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [('file', ('split_part.pdf', pdf_bytes, 'application/pdf'))]
    headers = {
        'X-OCR-SECRET': Config.OCR_SECRET_KEY
    }

    response = requests.post(Config.OCR_API_INVOKE_URL, headers=headers, data=payload, files=files)
    response_text = ""
    if response.status_code == 200:
        # OCR 응답에서 텍스트 추출
        for j in response.json().get('images', []):
            for i in j.get('fields', []):
                response_text += i.get('inferText', '') + " "
    else:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {response.status_code}")
    return response_text

def parse_ocr_text(text: str) -> Dict:
    """
    OCR로 추출한 텍스트를 파싱하여 학년별 데이터를 반환
    """

    # 불필요한 정보를 제외하기 위한 패턴 정의 (정확히 문서확인번호와 신청인 제거)
    exclude_pattern = re.compile(
        r"문서확인번호:\s*\d+-\d+-\d+-\d+\s*\(신청인:\s*[\S\s]+?\)\s*|"
        r"문서확인번호:\s*\d+-\d+-\d+-\d+\s*\(신청인\s*:\s*.*?\)\s*|"
        r"정부24\s+gov\.kr|"
        r"\S+고등학교\s*\d{4}년\s*\d{1,2}월\s*\d{1,2}일\s*\d+/\d+\s*반\s*\d+\s*번호\s*\d+\s*이름\s*\S+|"
        r"본\s증명서는\s열람용이며,\s법적\s효력이\s없습니다\."
    )

    # 각 섹션을 구분하는 패턴 정의 (띄어쓰기 유무를 모두 허용하도록 수정)
    pattern = re.compile(
        r"(1\.\s*인적\s*사항)(.*?)(?=2\.\s*학적\s*사항|$)|"
        r"(2\.\s*학적\s*사항)(.*?)(?=3\.\s*출결\s*상황|$)|"
        r"(3\.\s*출결\s*상황)(.*?)(?=4\.\s*수\s*상\s*경\s*력|$)|"
        r"(4\.\s*수\s*상\s*경\s*력)(.*?)(?=5\.\s*자격증\s*및\s*인증\s*취득\s*상황|$)|"
        r"(5\.\s*자격증\s*및\s*인증\s*취득\s*상황)(.*?)(?=6\.\s*진로\s*희망\s*사항|$)|"
        r"(6\.\s*진로\s*희망\s*사항)(.*?)(?=7\.\s*창의적\s*체험\s*활동\s*상황|$)|"
        r"(7\.\s*창의적\s*체험\s*활동\s*상황)(.*?)(?=8\.\s*교과\s*학습\s*발달\s*상황|$)|"
        r"(8\.\s*교과\s*학습\s*발달\s*상황)(.*?)(?=9\.\s*독서\s*활동\s*상황|$)|"
        r"(9\.\s*독서\s*활동\s*상황)(.*?)(?=10\.\s*행동\s*특성\s*및\s*종합\s*의견|$)|"
        r"(10\.\s*행동\s*특성\s*및\s*종합\s*의견)(.*?)(?=$)",
        re.DOTALL
    )

    # 매칭 결과 저장할 딕셔너리 초기화
    split_text = {
        "인적사항": "",
        "학적사항": "",
        "출결사항": "",
        "수상경력": "",
        "자격증 및 인증 취득상황": "",
        "진로희망사항": "",
        "창의적 체험활동상황": "",
        "교과학습발달상황": "",
        "독서활동상황": "",
        "행동특성 및 종합의견": ""
    }

    # 패턴으로 텍스트를 분리하여 딕셔너리에 저장
    for match in pattern.finditer(text):
        # 매칭된 그룹 중 None이 아닌 첫 번째 그룹을 사용하여 섹션 내용 추출
        section_content = next((match.group(i) for i in range(2, 21, 2) if match.group(i)), "").strip()

        # 불필요한 정보 제외
        section_content = exclude_pattern.sub("", section_content).strip()

        # 각 섹션에 맞는 내용 저장
        if match.group(1):
            split_text["인적사항"] = section_content
        elif match.group(3):
            split_text["학적사항"] = section_content
        elif match.group(5):
            split_text["출결사항"] = section_content
        elif match.group(7):
            split_text["수상경력"] = section_content
        elif match.group(9):
            split_text["자격증 및 인증 취득상황"] = section_content
        elif match.group(11):
            split_text["진로희망사항"] = section_content
        elif match.group(13):
            split_text["창의적 체험활동상황"] = section_content
        elif match.group(15):
            split_text["교과학습발달상황"] = section_content
        elif match.group(17):
            split_text["독서활동상황"] = section_content
        elif match.group(19):
            split_text["행동특성 및 종합의견"] = section_content

    split_text["교과학습발달상황"] = parse_academic_performance(split_text["교과학습발달상황"])

    return split_text


def parse_academic_performance(text: str) -> Dict:

    # 학년별 데이터를 저장할 딕셔너리 초기화
    grades_data = defaultdict(lambda: {
        "성적": [],
        "세부능력 및 특기사항": [],
        "체육 및 예술": [],
        "특기사항": []
    })

    # 학년별 패턴 정의 (1학년, 2학년, 3학년) 각각을 추출
    grade_pattern = re.compile(r"\[(\d학년)\](.*?)(?=(\[\d학년\]|$))", re.DOTALL)

    # 교과 과목 성적 데이터 패턴 정의
    subject_pattern = re.compile(
        r"(?P<교과>[\w()]+)\s(?P<과목>[^\s\d]+(?:\s[I]+)?)\s(?P<단위수>\d+)\s(?P<원점수_과목평균>\d+/[\d.]+)\((?P<표준편차>[\d.]+)\)\s("
        r"?P<성취도>[A-E])\((?P<수강자수>\d+)\)\s(?P<석차>\d+)",
        re.DOTALL
    )

    # 세부능력 및 특기사항, 체육 및 예술, 특기사항을 인식하기 위한 패턴 정의
    extra_pattern = re.compile(
        r"세부능력및특기사항(.*?)(?=<\s*체육\s*[·.]?\s*예술\s*\(음악/미술\)\s*>|세부능력및특기사항|특기사항|$)|"  # 세부능력 및 특기사항 (중복 허용)
        r"<\s*체육\s*[·.]?\s*예술\s*\(음악/미술\)\s*>(.*?)(?=특기사항|$)|"  # 체육 및 예술 패턴
        r"특기사항(.*?)(?=(\[\d학년\]|$))",  # 특기사항 패턴
        re.DOTALL
    )

    # 개별 과목별 세부능력 및 특기사항 패턴 정의
    individual_subject_pattern = re.compile(r"([가-힣]+(?:I{1,2}|[A-Z]?)?):\s*(.*?)(?=([가-힣]+(?:I{1,2}|[A-Z]?)?:|$))",
                                            re.DOTALL)

    # 체육 및 예술 섹션에서 학기별로 교과, 과목, 단위수, 성취도를 추출하는 패턴
    physical_arts_pattern = re.compile(
        r"(?P<교과>체육|예술\(음악/미술\))\s(?P<과목>.+?)\s(?P<단위수_1학기>\d+)\s(?P<성취도_1학기>[A-E])\s(?P<단위수_2학기>\d+)\s(?P<성취도_2학기>[A-E])",
        re.DOTALL
    )

    # 학년별로 데이터를 추출
    for grade_match in grade_pattern.finditer(text):
        grade = grade_match.group(1)  # 학년 (1학년, 2학년, ...)
        grade_text = grade_match.group(2)  # 해당 학년의 전체 텍스트

        # 교과 과목 성적 데이터를 추출
        for subject_match in subject_pattern.finditer(grade_text):
            subject_data = {
                "교과": subject_match.group("교과"),
                "과목": subject_match.group("과목"),
                "단위수": subject_match.group("단위수"),
                "원점수_과목평균": subject_match.group("원점수_과목평균"),
                "성취도": subject_match.group("성취도"),
                "석차": subject_match.group("석차"),
                "표준편차": subject_match.group("표준편차"),
                "수강자수": subject_match.group("수강자수"),
            }
            grades_data[grade]["성적"].append(subject_data)

        # 세부능력 및 특기사항, 체육 및 예술, 특기사항 추출
        extra_matches = extra_pattern.findall(grade_text)
        for match in extra_matches:
            if match[0]:  # 세부능력 및 특기사항이 여러 번 나타날 수 있음
                details = match[0].strip()
                for sub_match in individual_subject_pattern.finditer(details):
                    subject_name = sub_match.group(1)
                    subject_details = sub_match.group(2).strip()
                    formatted_details = f"{subject_name}: {subject_details}"
                    grades_data[grade]["세부능력 및 특기사항"].append(formatted_details)
            if match[1]:  # 체육 및 예술이 여러 번 나타날 수 있음
                physical_arts_text = match[1].strip()
                for physical_arts_match in physical_arts_pattern.finditer(physical_arts_text):
                    activity_data = {
                        "교과": physical_arts_match.group("교과"),
                        "과목": physical_arts_match.group("과목"),
                        "단위수_1학기": physical_arts_match.group("단위수_1학기"),
                        "성취도_1학기": physical_arts_match.group("성취도_1학기"),
                        "단위수_2학기": physical_arts_match.group("단위수_2학기"),
                        "성취도_2학기": physical_arts_match.group("성취도_2학기"),
                    }
                    grades_data[grade]["체육 및 예술"].append(activity_data)
            if match[2]:  # 특기사항이 여러 번 나타날 수 있음
                grades_data[grade]["특기사항"].append(match[2].strip())

    return grades_data