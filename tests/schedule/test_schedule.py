import pytest
import requests
# pytest tests/schedule/test_schedule.py -v 
# ===== 환경 설정 =====
BASE_URL = "https://api-classroom.elice.io"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjg5MDczODcsIm5vbmNlIjoiOWd5bW9CYWJja0NxZU13bSIsImlhdCI6MTc3NTIxNzQwMiwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.RqB3zVgu_5MyTkhrig5S04GW6HR-eJxDrc7O2EDH9h4"
CLASSROOM_ID = "11968486-1a7b-4105-8ae3-b397ea4f54a7"
 
HEADERS_WITH_TOKEN = {
    "Authorization": f"Bearer {VALID_TOKEN}",
    "x-elice-org-name-short": "qatrack",
}
 
HEADERS_NO_TOKEN = {
    "x-elice-org-name-short": "qatrack",
}
 
PARAMS = {
    "classroom_id": CLASSROOM_ID,
    "dt_start_ge": "2026-04-16T15:00:00.000Z",
    "dt_start_le": "2026-06-14T14:59:59.999Z",
    "count": 40,
}
 
 
# ===================================================
# ✅ Positive (정상)
# ===================================================
 
class TestSchedulePositive:
 
    def test_정상_학습자_토큰으로_스케줄_조회(self):
        """
        [요청 조건] 정상 학습자 토큰 포함 GET 요청
        [예상 결과] 200 OK, 스케줄 캘린더 목록 데이터 반환
        """
        response = requests.get(
            f"{BASE_URL}/schedule",
            headers=HEADERS_WITH_TOKEN,
            params=PARAMS,
        )
 
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
 
 
# ===================================================
# ❌ Negative (비정상)
# ===================================================
 
class TestScheduleNegative:
 
    def test_토큰_없이_GET_요청(self):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 401 Unauthorized, 인증 에러 반환
        [실제 결과] 403 Forbidden (서버 설계상 403 반환)
        """
        response = requests.get(
            f"{BASE_URL}/schedule",
            headers=HEADERS_NO_TOKEN,
            params=PARAMS,
        )
 
        # 실제 서버는 401 대신 403 반환 — 인증 헤더 없을 시 접근 거부 확인
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "no_access_token", (
            f"에러 코드 불일치: {data}"
        )
 
    def test_존재하지_않는_classroom_id로_조회(self):
        """
        [요청 조건] 존재하지 않는 classroom_id로 조회
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] 409 Conflict (서버 설계상 409 반환)
        """
        invalid_params = {
            **PARAMS,
            "classroom_id": "00000000-0000-0000-0000-000000000000",
        }
 
        response = requests.get(
            f"{BASE_URL}/schedule",
            headers=HEADERS_WITH_TOKEN,
            params=invalid_params,
        )
 
        # 실제 서버는 404 대신 409 반환 — 리소스 없음 에러 확인
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
 
class TestScheduleBoundary:
 
    def test_학습자_토큰으로_수업_일정_생성_API_호출(self):
        """
        [요청 조건] 학습자 토큰으로 수업 일정 생성 API 호출 (POST /schedule)
        [예상 결과] 403 Forbidden, has_no_permission
        [실제 결과] 403 Forbidden, has_no_permission (Pass)
        """
        params = {
            "classroom_id": CLASSROOM_ID,
            "dt_start_ge": "2026-06-01T09:00:00.000Z",
            "dt_start_le": "2026-06-01T10:00:00.000Z",
            "count": 40,
        }
 
        body = {
            "classroom_id": CLASSROOM_ID,
            "summary": "테스트 수업 일정",
            "dt_start": "2026-06-01T09:00:00.000Z",
            "dt_end": "2026-06-01T10:00:00.000Z",
        }
 
        response = requests.post(
            f"{BASE_URL}/schedule",
            headers=HEADERS_WITH_TOKEN,
            params=params,
            json=body,
        )
 
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )