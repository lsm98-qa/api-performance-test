import pytest
import requests
import os
from dotenv import load_dotenv

# pytest tests/course/test_classroom_course.py -v

load_dotenv()

# ===== 환경 설정 =====
CLASSROOM_ID = os.getenv("CLASSROOM_ID")
URL = f"https://api-classroom.elice.io/classroom/{CLASSROOM_ID}/course"

PARAMS = {
    "skip": 0,
    "count": 10,
}

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,ja;q=0.9,ko-KR;q=0.8,en-US;q=0.7,en;q=0.6",
    "origin": os.getenv("ORIGIN"),
    "priority": "u=1, i",
    "referer": f"{os.getenv('ORIGIN')}/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-elice-org-name-short": os.getenv("ORG_NAME_SHORT"),
}

VALID_TOKEN = os.getenv("VALID_TOKEN")
EXPIRED_TOKEN = os.getenv("EXPIRED_TOKEN")


# ===== Fixtures =====

@pytest.fixture
def valid_headers():
    """유효한 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {VALID_TOKEN}"}


@pytest.fixture
def no_auth_headers():
    """authorization 헤더가 없는 헤더"""
    return BASE_HEADERS


@pytest.fixture
def expired_headers():
    """만료된 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {EXPIRED_TOKEN}"}


# ===== Helper =====

def get_classroom_course(headers: dict) -> requests.Response:
    return requests.get(URL, headers=headers, params=PARAMS, timeout=10)


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestClassroomCoursePositive:

    def test_get_course_with_valid_token(self, valid_headers):
        """
        [요청 조건] 유효한 토큰 포함 GET 요청
        [예상 결과] 200 OK, 클래스룸 코스 목록 데이터 반환
        """
        # Given: 유효한 토큰이 포함된 헤더가 있을 때

        # When: 클래스룸 코스 목록 API를 호출한다
        response = get_classroom_course(valid_headers)

        # Then: 200 OK와 코스 데이터가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestClassroomCourseNegative:

    def test_get_course_without_token(self, no_auth_headers):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 403 Forbidden, 인증 에러 반환
        """
        # Given: authorization 헤더가 없는 상태일 때

        # When: 클래스룸 코스 목록 API를 호출한다
        response = get_classroom_course(no_auth_headers)

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )

    def test_get_course_with_expired_token(self, expired_headers):
        """
        [요청 조건] 만료된 토큰으로 GET 요청
        [예상 결과] 403 Forbidden, 인증 에러 반환
        """
        # Given: 만료된 토큰이 포함된 헤더가 있을 때

        # When: 클래스룸 코스 목록 API를 호출한다
        response = get_classroom_course(expired_headers)

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )