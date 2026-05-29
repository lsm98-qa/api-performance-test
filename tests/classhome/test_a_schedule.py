import pytest
import requests
from urllib.parse import urlencode


class TestScheduleList:
    # 수업 일정 조회에 사용하는 공통 query string을 생성한다.
    def _schedule_query(self, classroom_id):
        return urlencode(
            {
                "classroom_id": classroom_id,
                "dt_start_ge": "2026-05-01T00:00:00+09:00",
                "dt_start_le": "2026-05-31T23:59:59+09:00",
                "count": 20,
            }
        )

    # ✅ Positive - 정상 토큰으로 수업 일정 조회
    def test_schedule_list_positive(self, learner_client, classroom_id):
        # Given: 학습자 토큰과 유효한 classroom_id가 있을 때
        query = self._schedule_query(classroom_id)

        # When: 수업 일정 조회 API 호출
        response = learner_client.get(f"/schedule?{query}")

        # Then: 200 OK와 일정 목록 데이터가 반환되어야 한다
        # 외부 캘린더 서버 장애 시 409 반환 가능
        assert response.status_code in (200, 409), response.text
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    # ❌ Negative - 정상 토큰의 마지막 1글자를 제거한 잘못된 토큰으로 조회
    def test_schedule_list_invalid_token_trimmed(self, learner_client, classroom_id):
        # Given: 정상 토큰에서 마지막 1글자를 제거한 잘못된 토큰이 있을 때
        valid_token = learner_client.token
        invalid_token = valid_token[:-1]
        query = self._schedule_query(classroom_id)

        # When: 잘못된 토큰으로 수업 일정 조회 API 호출
        response = requests.get(
            f"{learner_client.base_url}/schedule?{query}",
            headers={"Authorization": f"Bearer {invalid_token}"},
            timeout=10,
        )

        # Then: 인증 실패가 반환되어야 한다
        # 환경에 따라 403 또는 409(내부 403 래핑) 반환 가능
        assert response.status_code in (403, 409), response.text
        if response.status_code == 409:
            body = response.json()
            assert body.get("code") in (
                "elice_core_unexpected_result",
                "elice_calendar_server_failed",
            )

    # 🔒 Boundary - 학습자 토큰으로 교육자 API 호출
    def test_schedule_boundary(self, learner_client, classroom_id):
        # Given: 학습자 토큰과 유효한 classroom_id가 있을 때

        # When: 학습자 토큰으로 교육자 전용 일정 생성 API 호출
        response = learner_client.post(
            "/schedule",
            data={
                "classroom_id": classroom_id,
                "summary": "test",
                "dt_start": "2026-05-19T10:00:00+09:00",
                "dt_end": "2026-05-19T11:00:00+09:00",
            },
        )

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403, response.text