import os

import pytest
import requests
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
    educator_client.headers = {
        **educator_client.headers,
        "x-elice-org-name-short": ORG_NAME_SHORT,
    }
    return educator_client


# ===== 헬퍼 =====
def course_bulk_endpoint(classroom_id=CLASSROOM_ID):
    """과목 일괄 추가 API 경로를 만든다."""
    return f"/v2/classroom/{classroom_id}/course/bulk"


def course_bulk_body(original_course_id=ORIGINAL_COURSE_ID):
    """원본 과목 ID를 과목 일괄 추가 요청 body 형식으로 만든다."""
    return {"original_course_ids": [original_course_id]}


def auth_headers(client, token):
    """기존 클라이언트 헤더에 원하는 토큰을 덮어쓴 인증 헤더를 만든다."""
    return {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }


def post_course_bulk_with_learner_token(qaproject_educator_client):
    """학습자 토큰으로 과목 일괄 추가 API를 직접 호출한다."""
    return requests.post(
        f"{qaproject_educator_client.base_url}{course_bulk_endpoint()}",
        headers=auth_headers(qaproject_educator_client, os.getenv("LEARNER_TOKEN")),
        json=course_bulk_body(),
        timeout=TIMEOUT,
    )


def assert_status(response, expected_status):
    """응답 상태코드가 예상값과 다르면 응답 본문까지 함께 보여준다."""
    assert response.status_code == expected_status, (
        f"expected: {expected_status}, actual: {response.status_code}\n"
        f"{response.text}"
    )


def assert_error_code(response, expected_code):
    """응답 JSON의 code 값이 예상 에러 코드와 같은지 확인한다."""
    data = response.json()
    assert data.get("code") == expected_code, (
        f"expected error code: {expected_code}, response: {data}"
    )


# ===================================================
# 정상
# ===================================================

class TestCourseBulkPositive:

    def test_post_course_bulk_with_educator_token(self, qaproject_educator_client):
        # When: 교육자 토큰으로 원본 과목을 현재 강의실에 일괄 추가한다.
        response = qaproject_educator_client.post(
            course_bulk_endpoint(),
            data=course_bulk_body(),
        )

        # Then: 과목 추가 요청이 정상 처리되어야 한다.
        assert_status(response, 200)


# ===================================================
# 비정상
# ===================================================

class TestCourseBulkNegative:

    def test_post_course_bulk_without_original_course_ids(
        self,
        qaproject_educator_client,
    ):
        # When: 필수값인 original_course_ids 없이 과목 일괄 추가를 요청한다.
        response = qaproject_educator_client.post(
            course_bulk_endpoint(),
            data={},
        )

        # Then: 필수값 누락으로 요청이 거부되어야 한다.
        assert_status(response, 422)


# ===================================================
# 권한
# ===================================================

class TestCourseBulkBoundary:

    def test_post_course_bulk_with_learner_token(self, qaproject_educator_client):
        # When: 학습자 토큰으로 교육자 전용 과목 추가 API를 호출한다.
        response = post_course_bulk_with_learner_token(qaproject_educator_client)

        # Then: 권한 없음 에러가 반환되어야 한다.
        assert_status(response, 403)
        assert_error_code(response, "has_no_permission")
