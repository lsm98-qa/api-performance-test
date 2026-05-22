import os
import requests

from dotenv import load_dotenv


# pytest tests/classroom_course/test_a_classroom_course.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
PARAMS = {
    "skip": 0,
    "count": 10,
}


# ===== 헬퍼 =====
def course_endpoint(classroom_id):
    """강의실 과목 목록 조회 경로를 생성한다."""
    return f"/classroom/{classroom_id}/course"


def expired_token_headers(learner_client):
    """만료된 토큰으로 요청하기 위한 헤더를 생성한다."""
    return {
        **learner_client.headers,
        "Authorization": f"Bearer {os.getenv('EXPIRED_TOKEN')}",
    }


def get_course_with_expired_token(learner_client, classroom_id):
    """만료된 토큰으로 과목 목록 조회 API를 호출한다."""
    return requests.get(
        f"{learner_client.base_url}{course_endpoint(classroom_id)}",
        headers=expired_token_headers(learner_client),
        params=PARAMS,
        timeout=TIMEOUT,
    )


# ===================================================
# 정상
# ===================================================

class TestClassroomCoursePositive:

    def test_get_course_with_valid_token(self, learner_client, classroom_id):
        """
        [요청 조건] 유효한 학습자 토큰 + classroom_id + skip + count
        [예상 결과] 200 정상 응답, 과목 목록 데이터 반환
        """
        # Given: 유효한 학습자 토큰과 과목 목록 조회 파라미터가 있을 때

        # When: 과목 목록 조회 API를 호출한다
        response = learner_client.get(
            course_endpoint(classroom_id),
            params=PARAMS,
        )

        # Then: 200 정상 응답이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 비정상
# ===================================================

class TestClassroomCourseNegative:

    def test_get_course_without_token(self, learner_client, classroom_id):
        """
        [요청 조건] 토큰 없이 과목 목록 조회 요청
        [예상 결과] 403 권한 없음, 인증 에러 반환
        """
        # Given: authorization 헤더가 없는 상태일 때

        # When: 토큰 없이 과목 목록 조회 API를 호출한다
        response = learner_client.get_no_token(
            course_endpoint(classroom_id),
            params=PARAMS,
        )

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )

    def test_get_course_with_expired_token(
        self,
        learner_client,
        classroom_id,
    ):
        """
        [요청 조건] 만료된 토큰으로 과목 목록 조회 요청
        [예상 결과] 403 권한 없음, 인증 에러 반환
        """
        # Given: 만료된 토큰 헤더와 과목 목록 조회 파라미터가 있을 때

        # When: 만료된 토큰으로 과목 목록 조회 API를 호출한다
        response = get_course_with_expired_token(
            learner_client,
            classroom_id,
        )

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
