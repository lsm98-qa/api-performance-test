import pytest
import requests
import os
from dotenv import load_dotenv

# pytest tests/course/test_classroom_course_delete.py -v

load_dotenv()

# ===== 환경 설정 =====
CLASSROOM_ID = os.getenv("CLASSROOM_ID_V2")
ORIGIN = os.getenv("ORIGIN_V2")
ORG_NAME_SHORT = os.getenv("ORG_NAME_SHORT_V2")
EDUCATOR_TOKEN = os.getenv("EDUCATOR_TOKEN")
OTHER_ORG_TOKEN = os.getenv("OTHER_ORG_TOKEN")
ORIGINAL_COURSE_ID = int(os.getenv("ORIGINAL_COURSE_ID"))

BASE_URL = "https://api-classroom.elice.io"
BULK_URL = f"{BASE_URL}/v2/classroom/{CLASSROOM_ID}/course/bulk"
LIST_URL = f"{BASE_URL}/classroom/{CLASSROOM_ID}/course"

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,ja;q=0.9,ko-KR;q=0.8,en-US;q=0.7,en;q=0.6",
    "origin": ORIGIN,
    "priority": "u=1, i",
    "referer": f"{ORIGIN}/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-elice-org-name-short": ORG_NAME_SHORT,
}


# ===== Fixtures =====

@pytest.fixture
def educator_headers():
    """교육자 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {EDUCATOR_TOKEN}"}


@pytest.fixture
def other_org_headers():
    """다른 기관 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {OTHER_ORG_TOKEN}"}


@pytest.fixture
def added_course_id(educator_headers):
    """
    삭제 테스트용 과목을 bulk로 추가하고 course_id를 반환하는 fixture
    - POST /v2/classroom/{classroom_id}/course/bulk 로 과목 추가
    - GET /classroom/{classroom_id}/course 로 추가된 course_id 확인
    """
    # Step 1: bulk로 과목 추가
    bulk_response = requests.post(
        BULK_URL,
        headers={**educator_headers, "content-type": "application/json"},
        json={"original_course_ids": [ORIGINAL_COURSE_ID]},
        timeout=10,
    )
    assert bulk_response.status_code == 200, (
        f"[Fixture] 과목 추가 실패: {bulk_response.status_code}\n{bulk_response.text}"
    )

    # Step 2: 추가된 course_id 확인
    list_response = requests.get(
        LIST_URL,
        headers=educator_headers,
        params={"skip": 0, "count": 10},
        timeout=10,
    )
    assert list_response.status_code == 200, (
        f"[Fixture] 과목 목록 조회 실패: {list_response.status_code}\n{list_response.text}"
    )

    courses = list_response.json().get("courses", [])
    course = next((c for c in courses if c.get("original_id") == ORIGINAL_COURSE_ID), None)
    assert course is not None, "[Fixture] 추가된 과목을 목록에서 찾을 수 없음"

    return course["id"]


# ===== Helper =====

def delete_classroom_course(course_id: int, headers: dict) -> requests.Response:
    url = f"{BASE_URL}/classroom/{CLASSROOM_ID}/course/{course_id}"
    return requests.delete(url, headers=headers, timeout=10)


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestClassroomCourseDeletePositive:

    def test_delete_course_with_educator_token(self, educator_headers, added_course_id):
        """
        [요청 조건] 교육자 토큰으로 과목 제거 DELETE 요청
        [예상 결과] 200 OK, 과목 정상 제거
        """
        # Given: 교육자 토큰과 추가된 course_id가 있을 때

        # When: 과목 삭제 API를 호출한다
        response = delete_classroom_course(added_course_id, educator_headers)

        # Then: 200 OK가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestClassroomCourseDeleteNegative:

    def test_delete_course_with_invalid_course_id(self, educator_headers):
        """
        [요청 조건] 교육자 토큰, 존재하지 않는 course_id로 DELETE 요청
        [예상 결과] 409 Conflict, model_not_found
        [실제 결과] 409 Conflict, elice_calendar_unexpected_result (model_not_found)
        """
        # Given: 존재하지 않는 course_id가 있을 때
        invalid_course_id = 00000000

        # When: 잘못된 course_id로 과목 삭제 API를 호출한다
        response = delete_classroom_course(invalid_course_id, educator_headers)

        # Then: 409 Conflict가 반환되어야 한다
        assert response.status_code == 409, (
            f"예상: 409, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "model_not_found", (
            f"에러 코드 불일치: {data}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestClassroomCourseDeleteBoundary:

    def test_delete_course_with_other_org_token(self, other_org_headers, added_course_id):
        """
        [요청 조건] 다른 기관 토큰으로 과목 제거 시도
        [예상 결과] 403 Forbidden, 기관 간 접근 차단
        [실제 결과] 200 OK, JSON 내에서 400 Bad Request를 반환하는 안티 패턴
        """
        # Given: 다른 기관 토큰과 추가된 course_id가 있을 때

        # When: 다른 기관 토큰으로 과목 삭제 API를 호출한다
        response = delete_classroom_course(added_course_id, other_org_headers)

        # Then: 403 Forbidden이 반환되어야 한다
        # 실제 서버는 200 OK로 응답하나 JSON body 내에서 400 반환하는 안티 패턴 확인
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )