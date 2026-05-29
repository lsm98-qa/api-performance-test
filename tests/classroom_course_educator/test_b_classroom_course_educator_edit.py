import os

import pytest
import requests
from dotenv import load_dotenv


# pytest tests/classroom_course_educator/test_b_classroom_course_educator_edit.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
ORG_NAME_SHORT = "qaproject"
OTHER_ORG_NAME_SHORT = "qatrack"
LECTURE_ID = int(os.getenv("LECTURE_ID"))
COURSE_ID = int(os.getenv("COURSE_ID_V2"))


# ===== 픽스처 =====
@pytest.fixture
def qaproject_educator_rest_client(educator_rest_client):
    """qaproject 기관 헤더를 사용하는 교육자 REST 클라이언트를 반환한다."""
    educator_rest_client.headers = {
        **educator_rest_client.headers,
        "x-elice-org-name-short": ORG_NAME_SHORT,
    }
    return educator_rest_client


# ===== 헬퍼 =====
def lecture_edit_endpoint():
    """강의 수정 API 경로를 만든다."""
    return f"/org/{ORG_NAME_SHORT}/lecture/edit/"


def lecture_edit_data(**overrides):
    """강의 수정 요청에 필요한 form data를 만든다."""
    data = {
        "is_opened": "true",
        "is_preview": "false",
        "description": "Test lecture description",
        "lecture_type": "0",
        "id": str(LECTURE_ID),
        "title": "[Test] Algorithm practice lecture",
        "depth": "1",
        "order_no": "1",
        "total_page_count": "4",
        "total_page_point": "400",
        "is_someone_test_started": "false",
        "main_lecture_pages": "[]",
        "sub_lecture_pages": "[]",
        "completed_page_count": "0",
        "progress_status": "0",
        "test_admission_status": "0",
        "test_user_status": "0",
        "is_page_readable": "true",
        "lecture_id": str(LECTURE_ID),
        "course_id": str(COURSE_ID),
    }
    data.update(overrides)
    return data


def org_headers(client, org_name_short):
    """기존 헤더에서 기관명 헤더만 원하는 값으로 바꾼다."""
    return {
        **client.headers,
        "x-elice-org-name-short": org_name_short,
    }


def post_lecture_edit_with_other_org(qaproject_educator_rest_client):
    """다른 기관 헤더로 강의 수정 API를 직접 호출한다."""
    return requests.post(
        f"{qaproject_educator_rest_client.base_url}{lecture_edit_endpoint()}",
        headers=org_headers(qaproject_educator_rest_client, OTHER_ORG_NAME_SHORT),
        data=lecture_edit_data(),
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

class TestLectureEditPositive:

    def test_edit_lecture_with_educator_token(self, qaproject_educator_rest_client):
        # When: 교육자 토큰으로 강의 수정 API를 호출한다.
        response = qaproject_educator_rest_client.post_form(
            lecture_edit_endpoint(),
            data=lecture_edit_data(),
        )

        # Then: 강의 수정 요청이 정상 처리되어야 한다.
        assert_status(response, 200)


# ===================================================
# 비정상
# ===================================================

class TestLectureEditNegative:

    def test_edit_lecture_without_title(self, qaproject_educator_rest_client):
        # Given: 필수값인 title을 제거한 강의 수정 데이터가 있다.
        form_data = lecture_edit_data()
        form_data.pop("title")

        # When: title 없이 강의 수정 API를 호출한다.
        response = qaproject_educator_rest_client.post_form(
            lecture_edit_endpoint(),
            data=form_data,
        )

        # Then: 필수값 누락으로 요청이 거부되어야 한다.
        assert_status(response, 400)


# ===================================================
# 권한
# ===================================================

class TestLectureEditBoundary:

    def test_edit_lecture_with_other_org_header(self, qaproject_educator_rest_client):
        # When: 다른 기관 헤더로 qaproject 강의 수정을 시도한다.
        response = post_lecture_edit_with_other_org(qaproject_educator_rest_client)

        # Then: 기관 권한이 맞지 않으므로 접근이 거부되어야 한다.
        assert_status(response, 403)
