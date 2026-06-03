import pytest


class TestClassroomDetail:
    # 공통 클래스 상세 API 경로를 생성한다.
    def _classroom_endpoint(self, classroom_id):
        return f"/classroom/{classroom_id}"

    # ✅ Positive - 정상 토큰으로 클래스 상세 조회
    def test_classroom_detail_positive(self, learner_client, classroom_id):
        # Given: 학습자 토큰과 유효한 classroom_id가 있을 때
        endpoint = self._classroom_endpoint(classroom_id)

        # When: 클래스 상세 조회 API 호출
        response = learner_client.get(endpoint)

        # Then: 200 OK와 클래스 데이터가 반환되어야 한다
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data

    # ❌ Negative - 토큰 없이 클래스 상세 조회
    def test_classroom_detail_no_token(self, learner_client, classroom_id):
        # Given: 토큰이 없는 상태일 때
        endpoint = self._classroom_endpoint(classroom_id)

        # When: 토큰 없이 클래스 상세 조회 API 호출
        response = learner_client.get_no_token(endpoint)

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403

    # 🔒 Boundary - 학습자 토큰으로 교육자 API 호출
    def test_classroom_detail_boundary(self, learner_client, classroom_id):
        # Given: 학습자 토큰이 있을 때
        endpoint = self._classroom_endpoint(classroom_id)

        # When: 학습자 토큰으로 교육자 전용 클래스 수정 API 호출
        response = learner_client.patch(endpoint, data={"name": "test"})

        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403