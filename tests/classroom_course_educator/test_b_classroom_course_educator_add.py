import pytest
import requests
import os
from dotenv import load_dotenv

# pytest tests/course/test_classroom_course_bulk.py -v

load_dotenv()

# ===== 환경 설정 =====
CLASSROOM_ID = os.getenv("CLASSROOM_ID_V2")
EDUCATOR_TOKEN = os.getenv("EDUCATOR_TOKEN")
LEARNER_TOKEN = os.getenv("LEARNER_TOKEN")
ORIGINAL_COURSE_ID = int(os.getenv("ORIGINAL_COURSE_ID"))

ORIGIN = "https://qaproject.elice.io"
ORG_NAME_SHORT = "qaproject"
URL = f"https://api-classroom.elice.io/v2/classroom/{CLASSROOM_ID}/course/bulk"

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,ja;q=0.9,ko-KR;q=0.8,en-US;q=0.7,en;q=0.6",
    "content-type": "application/json",
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


# ===== Fixtures =====

@pytest.fixture
def educator_headers():
    """교육자 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {EDUCATOR_TOKEN}"}


@pytest.fixture
def learner_headers():
    """학습자 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {LEARNER_TOKEN}"}


# ===== Helper =====

def post_course_bulk(headers: dict, body: dict) -> requests.Response:
    return requests.post(URL, headers=headers, json=body, timeout=10)


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestCourseBulkPositive:

    def test_post_course_bulk_with_educator_token(self, educator_headers):
        """
        [요청 조건] 교육자 토큰으로 과목 추가 POST 요청
        [예상 결과] 200 OK, 과목 정상 추가
        """
        # Given: 교육자 토큰과 유효한 original_course_ids가 있을 때
        body = {"original_course_ids": [ORIGINAL_COURSE_ID]}

        # When: 과목 bulk 추가 API를 호출한다
        response = post_course_bulk(educator_headers, body)

        # Then: 200 OK와 과목 추가 결과가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestCourseBulkNegative:

    def test_post_course_bulk_without_original_course_ids(self, educator_headers):
        """
        [요청 조건] 교육자 토큰, Body에 original_course_ids 누락
        [예상 결과] 422 Unprocessable Entity, 필수값 누락 에러 반환
        """
        # Given: original_course_ids가 없는 빈 body가 있을 때
        body = {}

        # When: 필수값 없이 과목 bulk 추가 API를 호출한다
        response = post_course_bulk(educator_headers, body)

        # Then: 422 Unprocessable Entity가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestCourseBulkBoundary:

    def test_post_course_bulk_with_learner_token(self, learner_headers):
        """
        [요청 조건] 학습자 토큰으로 과목 추가 시도
        [예상 결과] 403 Forbidden, has_no_permission
        """
        # Given: 학습자 토큰과 유효한 original_course_ids가 있을 때
        body = {"original_course_ids": [ORIGINAL_COURSE_ID]}

        # When: 학습자 토큰으로 과목 bulk 추가 API를 호출한다
        response = post_course_bulk(learner_headers, body)

        # Then: 권한 없음 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )