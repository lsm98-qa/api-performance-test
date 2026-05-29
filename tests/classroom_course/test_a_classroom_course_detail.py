import os

import requests
from dotenv import load_dotenv


# pytest tests/classroom_course/test_a_classroom_course_detail.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
COURSE_ID = os.getenv("COURSE_ID")


# ===== 헬퍼 =====
def course_detail_endpoint(classroom_id, course_id=COURSE_ID):
    """강의실의 특정 과목 상세 조회 API 경로를 만든다."""
    return f"/classroom/{classroom_id}/course/{course_id}"


def auth_headers(client, token):
    """기존 클라이언트 헤더에 원하는 토큰을 덮어쓴 인증 헤더를 만든다."""
    return {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }


def get_course_detail_with_expired_token(learner_client, classroom_id):
    """만료된 토큰으로 과목 상세 조회 API를 직접 호출한다."""
    return requests.get(
        f"{learner_client.base_url}{course_detail_endpoint(classroom_id)}",
        headers=auth_headers(learner_client, os.getenv("EXPIRED_TOKEN")),
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

class TestClassroomCourseDetailPositive:

    def test_get_course_detail_with_valid_token(self, learner_client, classroom_id):
        # When: 유효한 학습자 토큰으로 과목 상세 정보를 조회한다.
        response = learner_client.get(
            course_detail_endpoint(classroom_id),
        )

        # Then: 과목 상세 조회가 정상 처리되어야 한다.
        assert_status(response, 200)


# ===================================================
# 비정상
# ===================================================

class TestClassroomCourseDetailNegative:

    def test_get_course_detail_without_token(self, learner_client, classroom_id):
        # When: 토큰 없이 과목 상세 정보를 조회한다.
        response = learner_client.get_no_token(
            course_detail_endpoint(classroom_id),
        )

        # Then: 인증 정보가 없으므로 접근이 거부되어야 한다.
        assert_status(response, 403)

    def test_get_course_detail_with_expired_token(
        self,
        learner_client,
        classroom_id,
    ):
        # When: 만료된 토큰으로 과목 상세 정보를 조회한다.
        response = get_course_detail_with_expired_token(
            learner_client,
            classroom_id,
        )

        # Then: 유효하지 않은 토큰이므로 접근이 거부되어야 한다.
        assert_status(response, 403)
