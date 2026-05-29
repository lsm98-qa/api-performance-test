import os

import pytest
import requests
from dotenv import load_dotenv


# pytest tests/classroom_course_educator/test_b_classroom_course_educator_delete.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
CLASSROOM_ID = os.getenv("CLASSROOM_ID_V2")
ORG_NAME_SHORT = "qaproject"
OTHER_ORG_NAME_SHORT = "qatrack"
ORIGINAL_COURSE_ID = int(os.getenv("ORIGINAL_COURSE_ID"))
COURSE_LIST_PARAMS = {"skip": 0, "count": 10}


# ===== 헬퍼 =====
def course_endpoint(course_id=None, classroom_id=CLASSROOM_ID):
    """과목 목록 조회 또는 특정 과목 삭제 API 경로를 만든다."""
    endpoint = f"/classroom/{classroom_id}/course"
    if course_id is not None:
        return f"{endpoint}/{course_id}"
    return endpoint


def course_bulk_endpoint(classroom_id=CLASSROOM_ID):
    """삭제 테스트 준비용 과목 일괄 추가 API 경로를 만든다."""
    return f"/v2/classroom/{classroom_id}/course/bulk"


def course_bulk_body(original_course_id=ORIGINAL_COURSE_ID):
    """삭제 테스트에 사용할 원본 과목 추가 요청 body를 만든다."""
    return {"original_course_ids": [original_course_id]}


def org_headers(client, org_name_short):
    """기존 헤더에서 기관명 헤더만 원하는 값으로 바꾼다."""
    return {
        **client.headers,
        "x-elice-org-name-short": org_name_short,
    }


def delete_course_with_other_org(qaproject_educator_client, course_id):
    """다른 기관 헤더로 과목 삭제 API를 직접 호출한다."""
    return requests.delete(
        f"{qaproject_educator_client.base_url}{course_endpoint(course_id)}",
        headers=org_headers(qaproject_educator_client, OTHER_ORG_NAME_SHORT),
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


# ===== 픽스처 =====
@pytest.fixture
def qaproject_educator_client(educator_client):
    """qaproject 기관 헤더를 사용하는 교육자 클라이언트를 반환한다."""
    educator_client.headers = org_headers(educator_client, ORG_NAME_SHORT)
    return educator_client


@pytest.fixture
def added_course_id(qaproject_educator_client):
    """삭제 테스트용 과목을 추가하고, 테스트 종료 후 정리한다."""
    # Given: 삭제할 과목을 만들기 위해 원본 과목 ID가 준비되어 있다.
    bulk_response = qaproject_educator_client.post(
        course_bulk_endpoint(),
        data=course_bulk_body(),
    )
    assert_status(bulk_response, 200)

    # When: 과목 목록에서 방금 추가한 과목을 찾는다.
    list_response = qaproject_educator_client.get(
        course_endpoint(),
        params=COURSE_LIST_PARAMS,
    )
    assert_status(list_response, 200)

    courses = list_response.json().get("courses", [])
    course = next(
        (item for item in courses if item.get("original_id") == ORIGINAL_COURSE_ID),
        None,
    )
    assert course is not None, "added course was not found in the course list"

    yield course["id"]

    # Then: 테스트 성공/실패와 관계없이 생성된 과목을 정리한다.
    qaproject_educator_client.delete(
        course_endpoint(course["id"]),
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
        # When: 교육자 토큰으로 삭제 테스트용 과목을 삭제한다.
        response = qaproject_educator_client.delete(
            course_endpoint(added_course_id),
        )

        # Then: 과목 삭제가 정상 처리되어야 한다.
        assert_status(response, 200)


# ===================================================
# 비정상
# ===================================================

class TestClassroomCourseDeleteNegative:

    def test_delete_course_with_invalid_course_id(self, qaproject_educator_client):
        # When: 존재하지 않는 course_id로 과목 삭제를 요청한다.
        response = qaproject_educator_client.delete(
            course_endpoint(0),
        )

        # Then: 찾을 수 없는 모델이라는 에러가 반환되어야 한다.
        assert_status(response, 409)
        assert_error_code(response, "model_not_found")


# ===================================================
# 권한
# ===================================================

class TestClassroomCourseDeleteBoundary:

    def test_delete_course_with_other_org_header(
        self,
        qaproject_educator_client,
        added_course_id,
    ):
        # When: 다른 기관 헤더로 qaproject 과목 삭제를 시도한다.
        response = delete_course_with_other_org(
            qaproject_educator_client,
            added_course_id,
        )

        # Then: 기관 권한이 맞지 않으므로 접근이 거부되어야 한다.
        assert_status(response, 403)
