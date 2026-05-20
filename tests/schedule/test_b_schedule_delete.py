# -*- coding: utf-8 -*-
import pytest
import os
import requests as req
from dotenv import load_dotenv
# pytest tests/schedule/test_b_schedule_delete.py -v

load_dotenv()

# ===== 환경 설정 =====
EDUCATOR_CLASSROOM_ID = os.getenv("EDUCATOR_CLASSROOM_ID")
LEARNER_CLASSROOM_ID = os.getenv("LEARNER_CLASSROOM_ID")


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestScheduleDeletePositive:

    def test_schedule_delete_positive(self, educator_client, educator_schedule_id):
        """
        [요청 조건] 교육자 토큰 + 유효한 schedule_id + 유효한 classroom_id
        [예상 결과] 200 OK, 스케줄 삭제 완료
        [실제 결과] 200 OK, 스케줄 삭제 완료 (응답 Body: {})
        """
        # Given: 교육자 토큰과 유효한 스케줄 ID가 있을 때
        body = {"classroom_id": EDUCATOR_CLASSROOM_ID}

        # When: 스케줄 삭제 API 호출
        response = educator_client.delete(
            f"/schedule/{educator_schedule_id}",
            data=body,
        )

        # Then: 200 OK와 스케줄이 정상 삭제되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestScheduleDeleteNegative:

    def test_schedule_delete_invalid_schedule_id(self, educator_client):
        """
        [요청 조건] 교육자 토큰 + 존재하지 않는 schedule_id + 유효한 classroom_id
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] 409 Conflict, elice_calendar_unexpected_result (model_not_found)
        """
        # Given: 존재하지 않는 schedule_id가 있을 때
        body = {"classroom_id": EDUCATOR_CLASSROOM_ID}

        # When: 존재하지 않는 schedule_id로 스케줄 삭제 API 호출
        response = educator_client.delete(
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


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestScheduleDeleteBoundary:

    def test_schedule_delete_different_org(self, educator_client, educator_schedule_id):
        """
        [요청 조건] qaproject 토큰 + qatrack classroom_id로 스케줄 삭제 시도
        [예상 결과] 403 Forbidden, 기관 간 접근 차단
        [실제 결과] 403 Forbidden, has_no_permission (You have no permission)
        """
        # Given: 다른 기관 헤더로 스케줄 삭제 시도
        headers = {
            **educator_client.headers,
            "x-elice-org-name-short": "qatrack",
        }

        # When: 다른 기관 org로 스케줄 삭제 API 호출
        response = req.delete(
            f"{educator_client.base_url}/schedule/{educator_schedule_id}",
            headers=headers,
            json={"classroom_id": LEARNER_CLASSROOM_ID},
            timeout=10,
        )

        # Then: 기관 간 접근 차단 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "has_no_permission", (
            f"에러 코드 불일치: {data}"
        )