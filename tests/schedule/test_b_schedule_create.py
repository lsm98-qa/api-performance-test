# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/schedule/test_b_schedule_create.py -v

load_dotenv()

# ===== 환경 설정 =====
EDUCATOR_CLASSROOM_ID = os.getenv("EDUCATOR_CLASSROOM_ID")
LEARNER_CLASSROOM_ID = os.getenv("LEARNER_CLASSROOM_ID")


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestScheduleCreatePositive:

    def test_schedule_create_positive(self, educator_client):
        """
        [테스트 의도] 교육자가 수업 일정 생성 시 유효한 파라미터로 스케줄이 정상 생성되는지 검증
        [요청 조건] 교육자 토큰 + 유효한 classroom_id + summary + dt_start + dt_end
        [예상 결과] 200 OK, 스케줄 정상 생성
        [실제 결과] 200 OK, 스케줄 정상 생성
        """
        # Given: 교육자 토큰과 유효한 스케줄 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "summary": "교육자 테스트 수업",
            "dt_start": "2026-06-01T09:00:00.000Z",
            "dt_end": "2026-06-01T10:00:00.000Z",
        }

        # When: 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 200 OK와 스케줄이 정상 생성되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


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
            "dt_start": "2026-06-01T09:00:00.000Z",
            "dt_end": "2026-06-01T10:00:00.000Z",
        }

        # When: summary 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )

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
            "dt_end": "2026-06-01T10:00:00.000Z",
        }

        # When: dt_start 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )

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
            "dt_start": "2026-06-01T09:00:00.000Z",
        }

        # When: dt_end 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )

    def test_schedule_create_missing_classroom_id(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + summary + dt_start + dt_end (classroom_id 누락)
        [예상 결과] 400 Bad Request 또는 422, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, classroom_id Field required
        """
        # Given: classroom_id가 없는 스케줄 데이터가 있을 때
        body = {
            "summary": "교육자 테스트 수업",
            "dt_start": "2026-06-01T09:00:00.000Z",
            "dt_end": "2026-06-01T10:00:00.000Z",
        }

        # When: classroom_id 없이 스케줄 생성 API 호출
        response = educator_client.post("/schedule", data=body)

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )

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
            "dt_start": "2026-06-01T10:00:00.000Z",
            "dt_end": "2026-06-01T09:00:00.000Z",
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
            "dt_start": "2026-06-01T09:00:00.000Z",
            "dt_end": "2026-06-01T10:00:00.000Z",
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