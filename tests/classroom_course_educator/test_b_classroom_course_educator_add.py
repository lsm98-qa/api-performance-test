import os
import requests

import pytest
from dotenv import load_dotenv


# pytest tests/classroom_course_educator/test_b_classroom_course_educator_add.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
CLASSROOM_ID = os.getenv("CLASSROOM_ID_V2")
ORG_NAME_SHORT = "qaproject"
ORIGINAL_COURSE_ID = int(os.getenv("ORIGINAL_COURSE_ID"))


# ===== 픽스처 =====
@pytest.fixture
def qaproject_educator_client(educator_client):
    """qaproject 기관 헤더를 사용하는 교육자 클라이언트를 반환한다."""
    educator_client.headers["x-elice-org-name-short"] = ORG_NAME_SHORT
    return educator_client


# ===== 헬퍼 =====
def course_bulk_endpoint():
    """과목 일괄 추가 경로를 생성한다."""
    return f"/v2/classroom/{CLASSROOM_ID}/course/bulk"


def course_bulk_body():
    """과목 일괄 추가 요청 body를 생성한다."""
    return {"original_course_ids": [ORIGINAL_COURSE_ID]}


def learner_token_headers(qaproject_educator_client):
    """학습자 토큰으로 요청하기 위한 헤더를 생성한다."""
    return {
        **qaproject_educator_client.headers,
        "Authorization": f"Bearer {os.getenv('LEARNER_TOKEN')}",
    }


def post_course_bulk_with_learner_token(qaproject_educator_client):
    """학습자 토큰으로 과목 일괄 추가 API를 호출한다."""
    return requests.post(
        f"{qaproject_educator_client.base_url}{course_bulk_endpoint()}",
        headers=learner_token_headers(qaproject_educator_client),
        json=course_bulk_body(),
        timeout=TIMEOUT,
    )


# ===================================================
# 정상
# ===================================================

class TestCourseBulkPositive:

    def test_post_course_bulk_with_educator_token(self, qaproject_educator_client):
        """
        [요청 조건] 교육자 토큰 + 유효한 original_course_ids
        [예상 결과] 200 정상 응답, 과목 정상 추가
        """
        # Given: 교육자 토큰과 유효한 과목 추가 요청 body가 있을 때

        # When: 과목 일괄 추가 API를 호출한다
        response = qaproject_educator_client.post(
            course_bulk_endpoint(),
            data=course_bulk_body(),
        )

        # Then: 200 정상 응답이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 비정상
# ===================================================

class TestCourseBulkNegative:

    def test_post_course_bulk_without_original_course_ids(
        self,
        qaproject_educator_client,
    ):
        """
        [요청 조건] 교육자 토큰 + original_course_ids 누락
        [예상 결과] 422 처리할 수 없는 요청, 필수값 누락 에러 반환
        """
        # Given: original_course_ids가 없는 빈 body가 있을 때

        # When: 필수값 없이 과목 일괄 추가 API를 호출한다
        response = qaproject_educator_client.post(
            course_bulk_endpoint(),
            data={},
        )

        # Then: 422 처리할 수 없는 요청이 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 권한
# ===================================================

class TestCourseBulkBoundary:

    def test_post_course_bulk_with_learner_token(self, qaproject_educator_client):
        """
        [요청 조건] 학습자 토큰으로 과목 추가 시도
        [예상 결과] 403 권한 없음, has_no_permission 반환
        """
        # Given: 학습자 토큰과 유효한 과목 추가 요청 body가 있을 때

        # When: 학습자 토큰으로 과목 일괄 추가 API를 호출한다
        response = post_course_bulk_with_learner_token(qaproject_educator_client)

        # Then: 권한 없음 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )
