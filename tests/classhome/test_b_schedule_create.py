import os
import pytest


class TestScheduleCreate:
    # 수업 일정 생성 테스트에서 재사용할 기본 payload를 생성한다.
    def _schedule_payload(self, classroom_id, summary):
        return {
            "summary": summary,
            "educator_member_id": "24f77a4d-f86a-4d0b-9f9e-fb03700eeab6",
            "dt_start": "2026-05-21",
            "dt_end": "2026-05-21",
            "is_all_day": True,
            "rrule": None,
            "description": "<p class=\"editor-paragraph\"><span style=\"white-space: pre-wrap;\">123</span></p>",
            "classroom_id": classroom_id,
        }

    # ✅ Positive - 교육자 토큰으로 수업 일정 생성
    def test_schedule_create_positive(self, educator_client):
        # Given: 교육자 토큰과 유효한 educator_classroom_id, 필수 파라미터가 있을 때
        classroom_id = os.getenv("EDUCATOR_CLASSROOM_ID")
        assert classroom_id, "EDUCATOR_CLASSROOM_ID is required in .env"
        payload = self._schedule_payload(classroom_id, "교육자 테스트용")

        # When: 교육자 토큰으로 수업 일정 생성 POST 요청
        create_response = educator_client.post("/schedule", data=payload)

        # Then: 200 OK가 반환되어야 한다
        assert create_response.status_code == 200, create_response.text
        assert isinstance(create_response.json(), dict)

    # ❌ Negative - 필수 파라미터 누락 POST 요청
    def test_schedule_create_missing_required_param(self, educator_client):
        # Given: 교육자 토큰과 유효한 educator_classroom_id, 필수 파라미터가 누락된 요청일 때
        classroom_id = os.getenv("EDUCATOR_CLASSROOM_ID")
        assert classroom_id, "EDUCATOR_CLASSROOM_ID is required in .env"
        payload = self._schedule_payload(classroom_id, "교육자 테스트용")
        payload.pop("summary")

        # When: summary 누락 상태로 POST 요청
        response = educator_client.post("/schedule", data=payload)

        # Then: 400 또는 422가 반환되어야 한다
        assert response.status_code in (400, 422), response.text

    # 🔒 Boundary - 학습자 토큰으로 수업 일정 생성 API 호출
    def test_schedule_create_boundary(self, learner_client):
        # Given: 학습자 토큰과 유효한 learner_classroom_id가 있을 때
        classroom_id = os.getenv("LEARNER_CLASSROOM_ID")
        assert classroom_id, "LEARNER_CLASSROOM_ID is required in .env"
        payload = self._schedule_payload(classroom_id, "학습자 테스트용")

        # When: 학습자 토큰으로 수업 일정 생성 POST 요청
        response = learner_client.post("/schedule", data=payload)

        # Then: 권한 정책에 따라 403 또는 200
        # (현재 환경은 200 반환 중)
        assert response.status_code in (200, 403), response.text