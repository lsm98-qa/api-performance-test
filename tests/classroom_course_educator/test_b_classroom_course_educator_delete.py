import os
import requests

import pytest
from dotenv import load_dotenv


# pytest tests/classroom_course_educator/test_b_classroom_course_educator_delete.py -v

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


@pytest.fixture
def added_course_id(qaproject_educator_client):
    """삭제 테스트용 과목을 추가하고, 테스트 후 정리한다."""
    # Given: 삭제 테스트에 사용할 원본 과목 ID가 있을 때

    # When: 과목 일괄 추가 API를 호출한다
    bulk_response = qaproject_educator_client.post(
        course_bulk_endpoint(),
        data=course_bulk_body(),
    )
    assert bulk_response.status_code == 200, (
        f"[픽스처] 과목 추가 실패: {bulk_response.status_code}\n"
        f"{bulk_response.text}"
    )

    # Then: 추가된 과목 ID를 목록 조회 결과에서 찾는다
    list_response = qaproject_educator_client.get(
        course_endpoint(),
        params={"skip": 0, "count": 10},
    )
    assert list_response.status_code == 200, (
        f"[픽스처] 과목 목록 조회 실패: {list_response.status_code}\n"
        f"{list_response.text}"
    )

    courses = list_response.json().get("courses", [])
    course = next(
        (item for item in courses if item.get("original_id") == ORIGINAL_COURSE_ID),
        None,
    )
    assert course is not None, "[픽스처] 추가된 과목을 목록에서 찾을 수 없음"

    yield course["id"]

    # 테스트가 실패하더라도 생성한 과목은 정리한다
    qaproject_educator_client.delete(
        course_endpoint(course["id"]),
    )


# ===== 헬퍼 =====
def course_endpoint(course_id=None):
    """과목 목록 또는 과목 삭제 경로를 생성한다."""
    endpoint = f"/classroom/{CLASSROOM_ID}/course"
    if course_id is not None:
        endpoint = f"{endpoint}/{course_id}"
    return endpoint


def course_bulk_endpoint():
    """과목 일괄 추가 경로를 생성한다."""
    return f"/v2/classroom/{CLASSROOM_ID}/course/bulk"


def course_bulk_body():
    """삭제 테스트용 과목 추가 요청 body를 생성한다."""
    return {"original_course_ids": [ORIGINAL_COURSE_ID]}


def other_org_headers(qaproject_educator_client):
    """다른 기관 헤더로 요청하기 위한 헤더를 생성한다."""
    return {
        **qaproject_educator_client.headers,
        "x-elice-org-name-short": "qatrack",
    }


def delete_course_with_other_org(qaproject_educator_client, course_id):
    """다른 기관 헤더로 과목 삭제 API를 호출한다."""
    return requests.delete(
        f"{qaproject_educator_client.base_url}{course_endpoint(course_id)}",
        headers=other_org_headers(qaproject_educator_client),
        timeout=TIMEOUT,
    )


# ===================================================
# 정상
# ===================================================

class TestClassroomCourseDeletePositive:

    def test_delete_course_with_educator_token(
        self,
        qaproject_educator_client,
        added_course_id,
    ):
        """
        [요청 조건] 교육자 토큰 + 유효한 course_id
        [예상 결과] 200 정상 응답, 과목 정상 삭제
        """
        # Given: 교육자 토큰과 삭제할 과목 ID가 있을 때

        # When: 과목 삭제 API를 호출한다
        response = qaproject_educator_client.delete(
            course_endpoint(added_course_id),
        )

        # Then: 200 정상 응답이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 비정상
# ===================================================

class TestClassroomCourseDeleteNegative:

    def test_delete_course_with_invalid_course_id(self, qaproject_educator_client):
        """
        [요청 조건] 교육자 토큰 + 존재하지 않는 course_id
        [예상 결과] 409 Conflict, model_not_found 반환
        """
        # Given: 존재하지 않는 course_id가 있을 때

        # When: 잘못된 course_id로 과목 삭제 API를 호출한다
        response = qaproject_educator_client.delete(
            course_endpoint(0),
        )

        # Then: 409 Conflict와 model_not_found가 반환되어야 한다
        assert response.status_code == 409, (
            f"예상: 409, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "model_not_found", (
            f"에러 코드 불일치: {data}"
        )


# ===================================================
# 권한
# ===================================================

class TestClassroomCourseDeleteBoundary:

    def test_delete_course_with_other_org_header(
        self,
        qaproject_educator_client,
        added_course_id,
    ):
        """
        [요청 조건] 다른 기관 헤더로 과목 삭제 시도
        [예상 결과] 403 권한 없음, 기관 간 접근 차단
        """
        # Given: qatrack 기관 헤더와 qaproject 과목 ID가 있을 때

        # When: 다른 기관 헤더로 과목 삭제 API를 호출한다
        response = delete_course_with_other_org(
            qaproject_educator_client,
            added_course_id,
        )

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
