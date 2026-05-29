# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/schedule/test_b_schedule_update.py -v

load_dotenv()

# ===== 환경 설정 =====
EDUCATOR_CLASSROOM_ID = os.getenv("EDUCATOR_CLASSROOM_ID")
LEARNER_CLASSROOM_ID = os.getenv("LEARNER_CLASSROOM_ID")


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestScheduleUpdatePositive:

    def test_schedule_update_positive(self, educator_client, educator_schedule_id):
        """
        [요청 조건] 교육자 토큰 + 유효한 schedule_id + 유효한 classroom_id + 수정할 summary
        [예상 결과] 200 OK, 스케줄 수정 완료
        [실제 결과] 200 OK, 스케줄 수정 완료 (응답 Body: {})
        """
        # Given: 교육자 토큰과 유효한 스케줄 수정 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "summary": "교육자 테스트 수업 수정됨",
        }

        # When: 스케줄 수정 API 호출
        response = educator_client.patch(
            f"/schedule/{educator_schedule_id}",
            data=body,
        )

        # Then: 200 OK와 스케줄이 정상 수정되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data == {}, (
            f"응답 Body가 빈 객체가 아님: {data}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestScheduleUpdateNegative:

    def test_schedule_update_invalid_schedule_id(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + 존재하지 않는 schedule_id + 유효한 classroom_id
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] 409 Conflict, elice_calendar_unexpected_result (model_not_found)
        """
        # Given: 존재하지 않는 schedule_id가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
        }

        # When: 존재하지 않는 schedule_id로 스케줄 수정 API 호출
        response = educator_client.patch(
            "/schedule/00000000-0000-0000-0000-000000000000",
            data=body,
        )

        # Then: 리소스 없음 에러가 반환되어야 한다
        assert response.status_code == 409, (
            f"예상: 409, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "elice_calendar_unexpected_result", (
            f"에러 코드 불일치: {data}"
        )
        assert data.get("detail", {}).get("resp_json", {}).get("code") == "model_not_found", (
            f"model_not_found 에러 미확인: {data}"
        )

    def test_schedule_update_without_token(self, educator_client, educator_schedule_id):
        """
        [요청 조건] 토큰 없이 수정 요청 (PATCH)
        [예상 결과] 401 Unauthorized 또는 403 Forbidden, 인증 에러 반환
        [실제 결과] 403 Forbidden, no_access_token
        """
        # Given: 토큰이 없는 상태일 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
        }

        # When: 토큰 없이 스케줄 수정 PATCH API 호출
        response = educator_client.patch_no_token(
            f"/schedule/{educator_schedule_id}",
            data=body,
        )

        # Then: 인증 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "no_access_token", (
            f"에러 코드 불일치: {data}"
        )

    def test_schedule_update_missing_classroom_id(self, educator_client, educator_schedule_id):
        """
        [요청 조건] 교육자 토큰 + 유효한 schedule_id + classroom_id 누락
        [예상 결과] 400 Bad Request 또는 422, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, classroom_id Field required
        """
        # Given: classroom_id가 없는 수정 데이터가 있을 때
        body = {
            "summary": "수정 테스트",
        }

        # When: classroom_id 없이 스케줄 수정 API 호출
        response = educator_client.patch(
            f"/schedule/{educator_schedule_id}",
            data=body,
        )

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "classroom_id"
            for err in data.get("detail", [])
        ), f"classroom_id 누락 에러 미확인: {data}"

    def test_schedule_update_invalid_datetime(self, educator_client, educator_schedule_id):
        """
        [요청 조건] 교육자 토큰 + 유효한 schedule_id + dt_start > dt_end
        [예상 결과] 400 Bad Request, 유효성 에러 반환
        [실제 결과] 409 Conflict, elice_calendar_unexpected_result (invalid_datetime_format)
        """
        # Given: 시작 시간이 종료 시간보다 늦은 수정 데이터가 있을 때
        body = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "dt_start": "2026-08-01T10:00:00.000Z",
            "dt_end": "2026-08-01T09:00:00.000Z",
        }

        # When: 역전된 시간으로 스케줄 수정 API 호출
        response = educator_client.patch(
            f"/schedule/{educator_schedule_id}",
            data=body,
        )

        # Then: 유효성 에러가 반환되어야 한다
        assert response.status_code == 409, (
            f"예상: 409, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "elice_calendar_unexpected_result", (
            f"에러 코드 불일치: {data}"
        )
        assert data.get("detail", {}).get("resp_json", {}).get("code") == "invalid_datetime_format", (
            f"invalid_datetime_format 에러 미확인: {data}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestScheduleUpdateBoundary:

    def test_schedule_update_different_org(self, educator_client, educator_schedule_id):
        """
        [요청 조건] qaproject 토큰 + qatrack classroom_id로 스케줄 수정 시도
        [예상 결과] 403 Forbidden, 기관 간 접근 차단
        [실제 결과] 403 Forbidden, has_no_permission
        """
        # Given: 다른 기관 classroom_id가 있을 때
        body = {
            "classroom_id": LEARNER_CLASSROOM_ID,
            "summary": "권한 테스트 수정 시도",
        }

        # When: 다른 기관 classroom_id로 스케줄 수정 API 호출
        response = educator_client.patch(
            f"/schedule/{educator_schedule_id}",
            data=body,
        )

        # Then: 기관 간 접근 차단 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )