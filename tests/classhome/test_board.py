import pytest


class TestArticleList:

    # ✅ Positive - 정상 토큰으로 게시판 목록 조회
    def test_article_list_positive(self, learner_client, classroom_id):
        # Given: 학습자 토큰과 유효한 classroom_id가 있을 때

        # When: 게시판 목록 조회 API 호출
        response = learner_client.get(f"/classroom/{classroom_id}/article?skip=0&count=20")

        # Then: 200 OK와 게시글 목록 데이터가 반환되어야 한다
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, (list, dict))

    # ❌ Negative - 잘못된 classroom_id 형식으로 게시판 목록 조회
    def test_article_list_invalid_classroom_id(self, learner_client):
        # Given: classroom_id 형식이 잘못된 값이 있을 때
        invalid_classroom_id = "invalid-id"

        # When: 잘못된 classroom_id로 게시판 목록 조회 API 호출
        response = learner_client.get(f"/classroom/{invalid_classroom_id}/article?skip=0&count=20")

        # Then: 422 Unprocessable Entity가 반환되어야 한다
        assert response.status_code == 422, response.text

    # 🔒 Boundary - 학습자 토큰으로 교육자 API 호출
    def test_article_boundary(self, learner_client, classroom_id):
        # Given: 학습자 토큰과 유효한 classroom_id가 있을 때

        # When: 학습자 토큰으로 교육자 전용 게시글 생성 API 호출
        response = learner_client.post(
            f"/classroom/{classroom_id}/article",
            data={
                "title": "test",
                "content": "test content",
            },
        )

        # Then: Method Not Allowed가 반환되어야 한다
        assert response.status_code == 405, response.text