import os
import requests

import pytest
from dotenv import load_dotenv


# pytest tests/student/test_a_student.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
BASE_URL_DASHBOARD = os.getenv("BASE_URL_DASHBOARD", "https://api-dashboard.elice.io")
STUDENT_ID = os.getenv("STUDENT_ID")

PARAMS = {
    "classroom_id": os.getenv("CLASSROOM_ID"),
    "offset": 0,
    "count": 10,
}


# ===== 픽스처 =====
@pytest.fixture
def dashboard_client(learner_client):
    """대시보드 API 호출을 위한 학습자 클라이언트를 반환한다."""
    learner_client.base_url = BASE_URL_DASHBOARD
    learner_client.headers["Authorization"] = f"Bearer {os.getenv('VALID_TOKEN')}"
    return learner_client


# ===== 헬퍼 =====
def student_course_endpoint():
    """학생 과목 목록 조회 경로를 생성한다."""
    return f"/student/{STUDENT_ID}/course"


def expired_token_headers(dashboard_client):
    """만료된 토큰으로 요청하기 위한 헤더를 생성한다."""
    return {
        **dashboard_client.headers,
        "Authorization": f"Bearer {os.getenv('EXPIRED_TOKEN')}",
    }


def get_student_course_with_expired_token(dashboard_client):
    """만료된 토큰으로 학생 과목 목록 API를 호출한다."""
    return requests.get(
        f"{dashboard_client.base_url}{student_course_endpoint()}",
        headers=expired_token_headers(dashboard_client),
        params=PARAMS,
        timeout=TIMEOUT,
    )


# ===================================================
# 정상
# ===================================================

class TestStudentCoursePositive:

    def test_get_student_course_with_valid_token(self, dashboard_client):
        """
        [요청 조건] 유효한 학습자 토큰 + classroom_id + offset + count
        [예상 결과] 200 정상 응답, 학생 과목 목록 데이터 반환
        """
        # Given: 유효한 학습자 토큰과 학생 과목 목록 조회 파라미터가 있을 때

        # When: 학생 과목 목록 API를 호출한다
        response = dashboard_client.get(
            student_course_endpoint(),
            params=PARAMS,
        )

        # Then: 200 정상 응답이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 비정상
# ===================================================

class TestStudentCourseNegative:

    def test_get_student_course_without_token(self, dashboard_client):
        """
        [요청 조건] 토큰 없이 학생 과목 목록 조회 요청
        [예상 결과] 403 권한 없음, 인증 에러 반환
        """
        # Given: authorization 헤더가 없는 상태일 때

        # When: 토큰 없이 학생 과목 목록 API를 호출한다
        response = dashboard_client.get_no_token(
            student_course_endpoint(),
            params=PARAMS,
        )

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )

    def test_get_student_course_with_expired_token(self, dashboard_client):
        """
        [요청 조건] 만료된 토큰으로 학생 과목 목록 조회 요청
        [예상 결과] 403 권한 없음, 인증 에러 반환
        """
        # Given: 만료된 토큰 헤더와 학생 과목 목록 조회 파라미터가 있을 때

        # When: 만료된 토큰으로 학생 과목 목록 API를 호출한다
        response = get_student_course_with_expired_token(dashboard_client)

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
