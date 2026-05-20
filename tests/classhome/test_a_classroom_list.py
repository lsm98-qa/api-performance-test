import pytest

class TestClassroomDetail:

    # ✅ Positive - 정상 토큰으로 클래스 상세 조회
    def test_classroom_detail_positive(self, learner_client, classroom_id):
        # Given: 학습자 토큰과 유효한 classroom_id가 있을 때
        
        # When: 클래스 상세 조회 API 호출
        response = learner_client.get(f"/classroom/{classroom_id}")
        
        # Then: 200 OK와 클래스 데이터가 반환되어야 한다
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data

    # ❌ Negative - 토큰 없이 클래스 상세 조회
    def test_classroom_detail_no_token(self, learner_client, classroom_id):
        # Given: 토큰이 없는 상태일 때
        
        # When: 토큰 없이 클래스 상세 조회 API 호출
        response = learner_client.get_no_token(f"/classroom/{classroom_id}")
        
        # Then: 403 Forbidden아 반환되어야 한다
        assert response.status_code == 403

    # 🔒 Boundary - 학습자 토큰으로 교육자 API 호출
    def test_classroom_detail_boundary(self, learner_client, classroom_id):
        # Given: 학습자 토큰이 있을 때
        
        # When: 학습자 토큰으로 교육자 전용 클래스 수정 API 호출
        response = learner_client.patch(
            f"/classroom/{classroom_id}",
            data={"name": "test"}
        )
        
        # Then: 403 Forbidden이 반환되어야 한다
        assert response.status_code == 403