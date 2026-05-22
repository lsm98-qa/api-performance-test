import os
import requests

import pytest
from dotenv import load_dotenv


# pytest tests/classroom_course_educator/test_b_classroom_course_educator_edit.py -v

load_dotenv()

# ===== 환경 설정 =====
TIMEOUT = 10
ORG_NAME_SHORT = "qaproject"
LECTURE_ID = int(os.getenv("LECTURE_ID"))
COURSE_ID = int(os.getenv("COURSE_ID_V2"))


# ===== 픽스처 =====
@pytest.fixture
def qaproject_educator_rest_client(educator_rest_client):
    """qaproject 기관 헤더를 사용하는 교육자 REST 클라이언트를 반환한다."""
    educator_rest_client.headers["x-elice-org-name-short"] = ORG_NAME_SHORT
    return educator_rest_client


# ===== 헬퍼 =====
def lecture_edit_endpoint():
    """강의 수정 경로를 생성한다."""
    return f"/org/{ORG_NAME_SHORT}/lecture/edit/"


def lecture_edit_data(**overrides):
    """강의 수정 요청 form data를 생성한다."""
    data = {
        "is_opened": "true",
        "is_preview": "false",
        "description": "테스트 강의 설명",
        "lecture_type": "0",
        "id": str(LECTURE_ID),
        "title": "[테스트] 알고리즘 실습 강의",
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


def other_org_headers(qaproject_educator_rest_client):
    """다른 기관 헤더로 요청하기 위한 헤더를 생성한다."""
    return {
        **qaproject_educator_rest_client.headers,
        "x-elice-org-name-short": "qatrack",
    }


def post_lecture_edit_with_other_org(qaproject_educator_rest_client):
    """다른 기관 헤더로 강의 수정 API를 호출한다."""
    return requests.post(
        f"{qaproject_educator_rest_client.base_url}{lecture_edit_endpoint()}",
        headers=other_org_headers(qaproject_educator_rest_client),
        data=lecture_edit_data(),
        timeout=TIMEOUT,
    )


# ===================================================
# 정상
# ===================================================

class TestLectureEditPositive:

    def test_edit_lecture_with_educator_token(self, qaproject_educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + 유효한 강의 수정 form data
        [예상 결과] 200 정상 응답, 강의 정상 수정
        """
        # Given: 교육자 토큰과 유효한 강의 수정 데이터가 있을 때

        # When: 강의 수정 API를 호출한다
        response = qaproject_educator_rest_client.post_form(
            lecture_edit_endpoint(),
            data=lecture_edit_data(),
        )

        # Then: 200 정상 응답이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 비정상
# ===================================================

class TestLectureEditNegative:

    def test_edit_lecture_without_title(self, qaproject_educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + title 누락
        [예상 결과] 400 잘못된 요청, 필수값 누락 에러 반환
        """
        # Given: title이 누락된 강의 수정 데이터가 있을 때
        form_data = lecture_edit_data()
        form_data.pop("title")

        # When: title 없이 강의 수정 API를 호출한다
        response = qaproject_educator_rest_client.post_form(
            lecture_edit_endpoint(),
            data=form_data,
        )

        # Then: 400 잘못된 요청이 반환되어야 한다
        assert response.status_code == 400, (
            f"예상: 400, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# 권한
# ===================================================

class TestLectureEditBoundary:

    def test_edit_lecture_with_other_org_header(self, qaproject_educator_rest_client):
        """
        [요청 조건] 다른 기관 헤더로 강의 수정 시도
        [예상 결과] 403 권한 없음, 기관 간 접근 차단
        """
        # Given: qatrack 기관 헤더와 qaproject 강의 수정 데이터가 있을 때

        # When: 다른 기관 헤더로 강의 수정 API를 호출한다
        response = post_lecture_edit_with_other_org(qaproject_educator_rest_client)

        # Then: 403 권한 없음이 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
