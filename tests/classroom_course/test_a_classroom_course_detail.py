import os
import requests

from dotenv import load_dotenv


# pytest tests/classroom_course/test_a_classroom_course_detail.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
COURSE_ID = os.getenv("COURSE_ID")


# ===== 헬퍼 =====
def course_detail_endpoint(classroom_id):
    """강의실 과목 상세 조회 경로를 생성한다."""
    return f"/classroom/{classroom_id}/course/{COURSE_ID}"


def expired_token_headers(learner_client):
    """만료된 토큰으로 요청하기 위한 헤더를 생성한다."""
    return {
        **learner_client.headers,
        "Authorization": f"Bearer {os.getenv('EXPIRED_TOKEN')}",
    }


def get_course_detail_with_expired_token(learner_client, classroom_id):
    """만료된 토큰으로 과목 상세 조회 API를 호출한다."""
    return requests.get(
        f"{learner_client.base_url}{course_detail_endpoint(classroom_id)}",
        headers=expired_token_headers(learner_client),
        timeout=TIMEOUT,
    )


# ===================================================
# 정상
# ===================================================

class TestClassroomCourseDetailPositive:

    def test_get_course_detail_with_valid_token(self, learner_client, classroom_id):
        """
        [요청 조건] 유효한 학습자 토큰 + 유효한 classroom_id + 유효한 course_id
        [예상 결과] 200 정상 응답, 과목 상세 데이터 반환
        """
        # Given: 유효한 학습자 토큰과 과목 상세 조회 경로가 있을 때

        # When: 과목 상세 조회 API를 호출한다
        response = learner_client.get(
            course_detail_endpoint(classroom_id),
        )

        # Then: 200 정상 응답이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 비정상
# ===================================================

class TestClassroomCourseDetailNegative:

    def test_get_course_detail_without_token(self, learner_client, classroom_id):
        """
        [요청 조건] 토큰 없이 과목 상세 조회 요청
        [예상 결과] 403 권한 없음, 인증 에러 반환
        """
        # Given: authorization 헤더가 없는 상태일 때

        # When: 토큰 없이 과목 상세 조회 API를 호출한다
        response = learner_client.get_no_token(
            course_detail_endpoint(classroom_id),
        )

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )

    def test_get_course_detail_with_expired_token(
        self,
        learner_client,
        classroom_id,
    ):
        """
        [요청 조건] 만료된 토큰으로 과목 상세 조회 요청
        [예상 결과] 403 권한 없음, 인증 에러 반환
        """
        # Given: 만료된 토큰 헤더와 과목 상세 조회 경로가 있을 때

        # When: 만료된 토큰으로 과목 상세 조회 API를 호출한다
        response = get_course_detail_with_expired_token(
            learner_client,
            classroom_id,
        )

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
