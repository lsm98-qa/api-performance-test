# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/schedule/test_schedule.py -v

load_dotenv()

# ===== 환경 설정 =====
PARAMS = {
    "classroom_id": os.getenv("CLASSROOM_ID"),
    "dt_start_ge": "2026-04-16T15:00:00.000Z",
    "dt_start_le": "2026-06-14T14:59:59.999Z",
    "count": 40,
}


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestSchedulePositive:

    def test_schedule_get_positive(self, learner_client):
        """
        [요청 조건] 정상 학습자 토큰 포함 GET 요청
        [예상 결과] 200 OK, 스케줄 캘린더 목록 데이터 반환
        """
        # Given: 유효한 학습자 토큰과 classroom_id가 있을 때
        params = PARAMS

        # When: 스케줄 조회 API 호출
        response = learner_client.get(
            "/schedule",
            params=params,
        )

        # Then: 200 OK와 스케줄 데이터가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestScheduleNegative:

    def test_schedule_get_without_token(self, learner_client):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 401 Unauthorized, 인증 에러 반환
        [실제 결과] 403 Forbidden (서버 설계상 403 반환)
        """
        # Given: 토큰이 없는 상태일 때
        params = PARAMS

        # When: 토큰 없이 스케줄 조회 API 호출
        response = learner_client.get_no_token(
            "/schedule",
            params=params,
        )

        # Then: 인증 에러가 반환되어야 한다
        # 실제 서버는 401 대신 403 반환 — 인증 헤더 없을 시 접근 거부 확인
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "no_access_token", (
            f"에러 코드 불일치: {data}"
        )

    def test_schedule_get_invalid_classroom_id(self, learner_client):
        """
        [요청 조건] 존재하지 않는 classroom_id로 조회
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] 409 Conflict (서버 설계상 409 반환)
        """
        # Given: 존재하지 않는 classroom_id가 있을 때
        invalid_params = {
            **PARAMS,
            "classroom_id": "00000000-0000-0000-0000-000000000000",
        }

        # When: 존재하지 않는 classroom_id로 스케줄 조회 API 호출
        response = learner_client.get(
            "/schedule",
            params=invalid_params,
        )

        # Then: 리소스 없음 에러가 반환되어야 한다
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

    def test_schedule_post_as_learner(self, learner_client):
        """
        [요청 조건] 학습자 토큰으로 수업 일정 생성 API 호출 (POST /schedule)
        [예상 결과] 403 Forbidden, has_no_permission
        [실제 결과] 403 Forbidden, has_no_permission (Pass)
        """
        # Given: 학습자 토큰과 수업 일정 생성 데이터가 있을 때
        params = {
            "classroom_id": os.getenv("CLASSROOM_ID"),
            "dt_start_ge": "2026-06-01T09:00:00.000Z",
            "dt_start_le": "2026-06-01T10:00:00.000Z",
            "count": 40,
        }
        body = {
            "classroom_id": os.getenv("CLASSROOM_ID"),
            "summary": "테스트 수업 일정",
            "dt_start": "2026-06-01T09:00:00.000Z",
            "dt_end": "2026-06-01T10:00:00.000Z",
        }

        # When: 학습자 토큰으로 수업 일정 생성 API 호출
        response = learner_client.post_with_params(
            "/schedule",
            params=params,
            data=body,
        )

        # Then: 권한 없음 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )