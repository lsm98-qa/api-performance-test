import pytest
import requests
 
URL = "https://api-dashboard.elice.io/student/8906962/lecture"
 
PARAMS = {
    "classroom_id": "11968486-1a7b-4105-8ae3-b397ea4f54a7",
    "course_id": 767828,
    "filter_lecture_id": 6652042,
    "offset": 0,
    "count": 1,
}
 
BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,ja;q=0.9,ko-KR;q=0.8,en-US;q=0.7,en;q=0.6",
    "origin": "https://qatrack.elice.io",
    "priority": "u=1, i",
    "referer": "https://qatrack.elice.io/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-elice-org-name-short": "qatrack",
}
 
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjg5MDY5NjIsIm5vbmNlIjoiN0hqdFh1SW9uaTFaODM2QyIsImlhdCI6MTc3Mzk2ODA5NCwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.1dIWoQNYnxatvI4fpPHHYMd3YzCouiNx6sz7tGv1hvU"
EXPIRED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjEyMzQ1Njc4LCJub25jZSI6ImV4cGlyZWROb25jZSIsImlhdCI6MTYwMDAwMDAwMCwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.invalidsignature"
 
 
# ── Fixtures ──────────────────────────────────────────────────────────────────
 
@pytest.fixture
def valid_headers():
    """유효한 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {VALID_TOKEN}"}
 
 
@pytest.fixture
def no_auth_headers():
    """authorization 헤더가 없는 헤더"""
    return BASE_HEADERS
 
 
@pytest.fixture
def expired_headers():
    """만료된 토큰이 포함된 헤더"""
    return {**BASE_HEADERS, "authorization": f"Bearer {EXPIRED_TOKEN}"}
 
 
# ── Helper ────────────────────────────────────────────────────────────────────
 
def get_student_lecture(headers: dict) -> requests.Response:
    return requests.get(URL, headers=headers, params=PARAMS, timeout=10)
 
 
# ── Tests ─────────────────────────────────────────────────────────────────────
 
class TestStudentLectureApi:
 
    def test_유효한_토큰으로_요청시_200을_반환한다(self, valid_headers):
        # Given: 유효한 토큰이 포함된 헤더
        # When: 학습자 강의 목록 API를 호출한다
        response = get_student_lecture(valid_headers)
 
        # Then: 200 OK를 반환한다
        assert response.status_code == 200
 
    def test_토큰_없이_요청시_403을_반환한다(self, no_auth_headers):
        # Given: authorization 헤더가 없는 헤더
        # When: 학습자 강의 목록 API를 호출한다
        response = get_student_lecture(no_auth_headers)
 
        # Then: 403 Forbidden을 반환한다
        assert response.status_code == 403
 
    def test_만료된_토큰으로_요청시_403을_반환한다(self, expired_headers):
        # Given: 만료된 토큰이 포함된 헤더
        # When: 학습자 강의 목록 API를 호출한다
        response = get_student_lecture(expired_headers)
 
        # Then: 403 Forbidden을 반환한다
        assert response.status_code == 403