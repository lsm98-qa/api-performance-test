import os
import pytest
import requests
from datetime import datetime


class TestClassroomUpdate:
    # 공통 클래스 상세 API 경로를 생성한다.
    def _classroom_endpoint(self, classroom_id):
        return f"/classroom/{classroom_id}"

    # ✅ Positive - 교육자 토큰으로 클래스 이름 수정
    def test_classroom_update_positive(self, educator_client):
        # Given: 교육자 토큰과 유효한 educator_classroom_id가 있을 때
        classroom_id = os.getenv("EDUCATOR_CLASSROOM_ID")
        assert classroom_id, "EDUCATOR_CLASSROOM_ID is required in .env"
        endpoint = self._classroom_endpoint(classroom_id)

        before_response = educator_client.get(endpoint)
        assert before_response.status_code == 200, before_response.text
        before_data = before_response.json()
        original_name = before_data["name"]
        updated_name = f"QA_API_UPDATE_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # When: 교육자 토큰으로 클래스 이름 수정 PATCH 요청
        patch_response = educator_client.patch(endpoint, data={"name": updated_name})

        # Then: 200 OK와 수정 반영 결과가 확인되어야 한다
        assert patch_response.status_code == 200, (
            "교육자 토큰 권한을 확인하세요. "
            f"현재 응답: {patch_response.status_code} / {patch_response.text}"
        )

        after_response = educator_client.get(endpoint)
        assert after_response.status_code == 200, after_response.text
        after_data = after_response.json()
        assert after_data["name"] == updated_name

        # 테스트 데이터 원복
        restore_response = educator_client.patch(endpoint, data={"name": original_name})
        assert restore_response.status_code == 200, restore_response.text

    # ❌ Negative - 토큰 없이 클래스 수정 요청
    def test_classroom_update_no_token(self, educator_client):
        # Given: 토큰이 없는 상태일 때
        classroom_id = os.getenv("EDUCATOR_CLASSROOM_ID")
        assert classroom_id, "EDUCATOR_CLASSROOM_ID is required in .env"
        endpoint = self._classroom_endpoint(classroom_id)

        # When: 토큰 없이 클래스 수정 PATCH 요청
        response = requests.patch(
            f"{educator_client.base_url}{endpoint}",
            json={"name": "NO_TOKEN_TRY"},
            timeout=10,
        )

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403, response.text

    # 🔒 Boundary - 학습자 토큰으로 교육자 전용 클래스 수정 API 호출
    def test_classroom_update_boundary(self, learner_client):
        # Given: 학습자 토큰과 유효한 learner_classroom_id가 있을 때
        classroom_id = os.getenv("LEARNER_CLASSROOM_ID")
        assert classroom_id, "LEARNER_CLASSROOM_ID is required in .env"
        endpoint = self._classroom_endpoint(classroom_id)

        # When: 학습자 토큰으로 클래스 수정 PATCH 요청
        response = learner_client.patch(endpoint, data={"name": "LEARNER_TRY_UPDATE"})

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403, response.text