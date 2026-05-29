import os

import pytest
import requests
from dotenv import load_dotenv


# pytest tests/student/test_a_student_lecture.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
BASE_URL_DASHBOARD = os.getenv("BASE_URL_DASHBOARD", "https://api-dashboard.elice.io")
STUDENT_ID = os.getenv("STUDENT_ID")
STUDENT_LECTURE_PARAMS = {
    "classroom_id": os.getenv("CLASSROOM_ID"),
    "course_id": int(os.getenv("COURSE_ID")),
    "filter_lecture_id": int(os.getenv("FILTER_LECTURE_ID")),
    "offset": 0,
    "count": 1,
}


# ===== 픽스처 =====
@pytest.fixture
def dashboard_client(learner_client):
    """대시보드 API 호출용 base_url과 학습자 토큰을 적용한 클라이언트를 반환한다."""
    learner_client.base_url = BASE_URL_DASHBOARD
    learner_client.headers = {
        **learner_client.headers,
        "Authorization": f"Bearer {os.getenv('VALID_TOKEN')}",
    }
    return learner_client


# ===== 헬퍼 =====
def student_lecture_endpoint(student_id=STUDENT_ID):
    """학생 강의 목록 조회 API 경로를 만든다."""
    return f"/student/{student_id}/lecture"


def auth_headers(client, token):
    """기존 클라이언트 헤더에 원하는 토큰을 덮어쓴 인증 헤더를 만든다."""
    return {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }


def get_student_lecture_with_expired_token(dashboard_client):
    """만료된 토큰으로 학생 강의 목록 조회 API를 직접 호출한다."""
    return requests.get(
        f"{dashboard_client.base_url}{student_lecture_endpoint()}",
        headers=auth_headers(dashboard_client, os.getenv("EXPIRED_TOKEN")),
        params=STUDENT_LECTURE_PARAMS,
        timeout=TIMEOUT,
    )


def assert_status(response, expected_status):
    """응답 상태코드가 예상값과 다르면 응답 본문까지 함께 보여준다."""
    assert response.status_code == expected_status, (
        f"expected: {expected_status}, actual: {response.status_code}\n"
        f"{response.text}"
    )


# ===================================================
# 정상
# ===================================================

class TestStudentLecturePositive:

    def test_get_student_lecture_with_valid_token(self, dashboard_client):
        # When: 유효한 학습자 토큰으로 학생 강의 목록을 조회한다.
        response = dashboard_client.get(
            student_lecture_endpoint(),
            params=STUDENT_LECTURE_PARAMS,
        )

        # Then: 학생 강의 목록 조회가 정상 처리되어야 한다.
        assert_status(response, 200)


# ===================================================
# 비정상
# ===================================================

class TestStudentLectureNegative:

    def test_get_student_lecture_without_token(self, dashboard_client):
        # When: 토큰 없이 학생 강의 목록을 조회한다.
        response = dashboard_client.get_no_token(
            student_lecture_endpoint(),
            params=STUDENT_LECTURE_PARAMS,
        )

        # Then: 인증 정보가 없으므로 접근이 거부되어야 한다.
        assert_status(response, 403)

    def test_get_student_lecture_with_expired_token(self, dashboard_client):
        # When: 만료된 토큰으로 학생 강의 목록을 조회한다.
        response = get_student_lecture_with_expired_token(dashboard_client)

        # Then: 유효하지 않은 토큰이므로 접근이 거부되어야 한다.
        assert_status(response, 403)
