# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/schedule/test_b_schedule_create.py -v

load_dotenv()

# ===== 환경 설정 =====
EDUCATOR_CLASSROOM_ID = os.getenv("EDUCATOR_CLASSROOM_ID")
LEARNER_CLASSROOM_ID = os.getenv("LEARNER_CLASSROOM_ID")
SCHEDULE_DT_START = os.getenv("SCHEDULE_CREATE_DT_START", "2026-06-01T09:00:00.000Z")
SCHEDULE_DT_END = os.getenv("SCHEDULE_CREATE_DT_END", "2026-06-01T10:00:00.000Z")


# ===== Fixture: 테스트용 스케줄 자동 생성 및 삭제 =====
@pytest.fixture
def created_schedule_id(educator_client):
    """Positive 테스트용 스케줄 생성 후 자동 삭제"""
    body = {
        "classroom_id": EDUCATOR_CLASSROOM_ID,
        "summary": "교육자 테스트 수업",
        "dt_start": SCHEDULE_DT_START,
        "dt_end": SCHEDULE_DT_END,
    }
    response = educator_client.post("/schedule", data=body)
    assert response.status_code == 200, f"스케줄 생성 실패: {response.text}"

    # 생성된 스케줄 ID 조회
    list_response = educator_client.get(
        "/schedule",
        params={
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "dt_start_ge": SCHEDULE_DT_START[:10] + "T00:00:00.000Z",
            "dt_start_le": SCHEDULE_DT_START[:10] + "T23:59:59.999Z",
            "count": 10,
        }
    )
    schedules = list_response.json()
    target = next((s for s in schedules if s.get("summary") == "교육자 테스트 수업"), None)
    assert target is not None, "생성된 스케줄을 찾을 수 없음"
    schedule_id = target["id"]

    yield schedule_id  # 테스트 실행

    # 테스트 후 자동 삭제
    educator_client.delete(
        f"/schedule/{schedule_id}",
        data={"classroom_id": EDUCATOR_CLASSROOM_ID},
    )


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestScheduleCreatePositive:

    def test_schedule_create_positive(self, educator_client, created_schedule_id):
        """
        [테스트 의도] 교육자가 수업 일정 생성 시 유효한 파라미터로 스케줄이 정상 생성되는지 검증
        [요청 조건] 교육자 토큰 + 유효한 classroom_id + summary + dt_start + dt_end
        [예상 결과] 200 OK, 스케줄 정상 생성
        [실제 결과] 200 OK, 스케줄 정상 생성
        """
        # Given: 교육자 토큰과 유효한 스케줄 데이터가 있을 때 (fixture로 자동 생성)

        # Then: 200 OK와 스케줄이 정상 생성되어야 한다
        assert created_schedule_id is not None, "스케줄 ID가 반환되지 않음"


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestScheduleCreateNegative:

    def test_schedule_create_missing_summary(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + classroom_id + dt_start + dt_end (summary 누락)
        [예상 결과] 400 Bad Request 또는 422, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, summary Field required
        """
        # Given: summary가 없는 스케줄 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "dt_start": SCHEDULE_DT_START,
            "dt_end": SCHEDULE_DT_END,
        }

        # When: summary 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "summary"
            for err in data.get("detail", [])
        ), f"summary 누락 에러 미확인: {data}"

    def test_schedule_create_missing_dt_start(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + classroom_id + summary + dt_end (dt_start 누락)
        [예상 결과] 400 Bad Request 또는 422, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, dt_start Field required
        """
        # Given: dt_start가 없는 스케줄 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "summary": "교육자 테스트 수업",
            "dt_end": SCHEDULE_DT_END,
        }

        # When: dt_start 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "dt_start"
            for err in data.get("detail", [])
        ), f"dt_start 누락 에러 미확인: {data}"

    def test_schedule_create_missing_dt_end(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + classroom_id + summary + dt_start (dt_end 누락)
        [예상 결과] 400 Bad Request 또는 422, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, dt_end Field required
        """
        # Given: dt_end가 없는 스케줄 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "summary": "교육자 테스트 수업",
            "dt_start": SCHEDULE_DT_START,
        }

        # When: dt_end 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "dt_end"
            for err in data.get("detail", [])
        ), f"dt_end 누락 에러 미확인: {data}"

    def test_schedule_create_missing_classroom_id(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + summary + dt_start + dt_end (classroom_id 누락)
        [예상 결과] 400 Bad Request 또는 422, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, classroom_id Field required
        """
        # Given: classroom_id가 없는 스케줄 데이터가 있을 때
        body = {
            "summary": "교육자 테스트 수업",
            "dt_start": SCHEDULE_DT_START,
            "dt_end": SCHEDULE_DT_END,
        }

        # When: classroom_id 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "classroom_id"
            for err in data.get("detail", [])
        ), f"classroom_id 누락 에러 미확인: {data}"

    def test_schedule_create_invalid_datetime(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + 시작 시간이 종료 시간보다 늦은 값 입력
        [예상 결과] 400 Bad Request, 유효성 에러 반환
        [실제 결과] 409 Conflict, elice_calendar_unexpected_result (invalid_datetime_format)
        """
        # Given: 시작 시간이 종료 시간보다 늦은 스케줄 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "summary": "교육자 테스트 수업",
            "dt_start": SCHEDULE_DT_END,   # 의도적으로 역전
            "dt_end": SCHEDULE_DT_START,
        }

        # When: 역전된 시간으로 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 유효성 에러가 반환되어야 한다
        assert response.status_code == 409, (
            f"예상: 409, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "elice_calendar_unexpected_result", (
            f"에러 코드 불일치: {data}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestScheduleCreateBoundary:

    def test_schedule_create_learner_token(self, learner_client):
        """
        [요청 조건] 학습자 토큰으로 스케줄 생성 시도
        [예상 결과] 403 Forbidden, has_no_permission
        [실제 결과] 403 Forbidden, has_no_permission
        """
        # Given: 학습자 토큰과 학습자 classroom_id로 스케줄 생성 시도
        body = {
            "classroom_id": LEARNER_CLASSROOM_ID,
            "summary": "테스트 수업 일정",
            "dt_start": SCHEDULE_DT_START,
            "dt_end": SCHEDULE_DT_END,
        }

        # When: 학습자 토큰으로 스케줄 생성 API 호출
        response = learner_client.post("/schedule", data=body)

        # Then: 권한 없음 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )