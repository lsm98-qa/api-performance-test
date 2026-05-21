import pytest
import requests
import os
from dotenv import load_dotenv

# pytest tests/lecture/test_lecture_edit.py -v

load_dotenv()

# ===== 환경 설정 =====
EDUCATOR_TOKEN = os.getenv("EDUCATOR_TOKEN")
LECTURE_ID = int(os.getenv("LECTURE_ID"))
COURSE_ID = int(os.getenv("COURSE_ID_V2"))

ORIGIN = "https://qaproject.elice.io"
ORG_NAME_SHORT = "qaproject"
URL = f"https://api-rest.elice.io/org/{ORG_NAME_SHORT}/lecture/edit/"

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,ja;q=0.9,ko-KR;q=0.8,en-US;q=0.7,en;q=0.6",
    "origin": ORIGIN,
    "priority": "u=1, i",
    "referer": f"{ORIGIN}/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-elice-org-name-short": ORG_NAME_SHORT,
}

VALID_FORM_DATA = {
    "is_opened": "true",
    "is_preview": "false",
    "description": "테스트 설명",
    "lecture_type": "0",
    "id": str(LECTURE_ID),
    "title": "[Test] 알고리즘 테스트 체험용 문항",
    "depth": "1",
    "order_no": "1",
    "total_page_count": "4",
    "total_page_point": "400",
    "is_someone_test_started": "false",
    "main_lecture_pages": "[]",
    "sub_lecture_pages": "[]",
    "completed_page_count": "0",
    "progress_status": "0",
    "test_admission_status": "0",
    "test_user_status": "0",
    "is_page_readable": "true",
    "lecture_id": str(LECTURE_ID),
    "course_id": str(COURSE_ID),
}


# ===== Fixtures =====

@pytest.fixture
def educator_headers():
    """교육자 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {EDUCATOR_TOKEN}"}


@pytest.fixture
def other_org_headers():
    """다른 기관 헤더 (x-elice-org-name-short만 qatrack으로 변경)"""
    return {
        **BASE_HEADERS,
        "authorization": f"Bearer {EDUCATOR_TOKEN}",
        "x-elice-org-name-short": "qatrack",
    }


# ===== Helper =====

def post_lecture_edit(headers: dict, form_data: dict) -> requests.Response:
    return requests.post(URL, headers=headers, data=form_data, timeout=10)


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestLectureEditPositive:

    def test_edit_lecture_with_educator_token(self, educator_headers):
        """
        [요청 조건] 교육자 토큰으로 강의 수정 POST 요청
        [예상 결과] 200 OK, 강의 정상 수정 및 업데이트된 강의 정보 반환
        """
        # Given: 교육자 토큰과 유효한 강의 수정 데이터가 있을 때

        # When: 강의 수정 API를 호출한다
        response = post_lecture_edit(educator_headers, VALID_FORM_DATA)

        # Then: 200 OK와 수정된 강의 정보가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestLectureEditNegative:

    def test_edit_lecture_without_title(self, educator_headers):
        """
        [요청 조건] 교육자 토큰, 필수 파라미터 title 누락
        [예상 결과] 400 Bad Request, 필수값 누락 에러 반환
        [실제 결과] 200 OK, JSON 내에서 400 Bad Request를 반환하는 안티 패턴
        """
        # Given: title이 누락된 form data가 있을 때
        form_data = {k: v for k, v in VALID_FORM_DATA.items() if k != "title"}

        # When: title 없이 강의 수정 API를 호출한다
        response = post_lecture_edit(educator_headers, form_data)

        # Then: 400 Bad Request가 반환되어야 한다
        # 실제 서버는 200 OK로 응답하나 JSON body 내에서 400 반환하는 안티 패턴 확인
        assert response.status_code == 400, (
            f"예상: 400, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestLectureEditBoundary:

    def test_edit_lecture_with_other_org_header(self, other_org_headers):
        """
        [요청 조건] 다른 기관 헤더(qatrack)로 강의 수정 시도
        [예상 결과] 403 Forbidden, 기관 간 접근 차단
        [실제 결과] 200 OK, JSON 내에서 400 Bad Request를 반환하는 안티 패턴
        """
        # Given: 다른 기관 헤더와 유효한 강의 수정 데이터가 있을 때

        # When: 다른 기관 헤더로 강의 수정 API를 호출한다
        response = post_lecture_edit(other_org_headers, VALID_FORM_DATA)

        # Then: 403 Forbidden이 반환되어야 한다
        # 실제 서버는 200 OK로 응답하나 JSON body 내에서 400 반환하는 안티 패턴 확인
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )