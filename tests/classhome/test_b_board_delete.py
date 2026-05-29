import os
import requests
import pytest


class TestBoardArticleDelete:
    # 게시글 삭제 API 공통 URL을 반환한다.
    def _delete_url(self):
        return "https://api-rest.elice.io/org/qaproject/board/article/delete/"
    
    # 토큰 유무에 따라 게시글 삭제 요청을 공통 방식으로 전송한다.
    def _post_delete(self, token, article_id):
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return requests.post(
            self._delete_url(),
            headers=headers,
            data={"board_article_id": article_id},
            timeout=10,
        )

    # ✅ Positive - 교육자 토큰으로 게시글 삭제
    def test_board_article_delete_positive(self):
        # Given: 교육자 토큰과 유효한 board_article_id가 있을 때
        article_id = os.getenv("BOARD_ARTICLE_ID")
        assert article_id, "BOARD_ARTICLE_ID is required in .env"

        # When: 교육자 토큰으로 게시글 삭제 요청
        response = self._post_delete(os.getenv("EDUCATOR_TOKEN"), article_id)

        # Then: 게시글 삭제가 성공해야 한다
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("_result", {}).get("status") == "ok", body

    # ❌ Negative - 토큰 없이 게시글 삭제 요청
    def test_board_article_delete_no_token(self):
        # Given: 토큰이 없는 상태일 때
        article_id = os.getenv("BOARD_ARTICLE_ID_NO_TOKEN")
        assert article_id, "BOARD_ARTICLE_ID_NO_TOKEN is required in .env"

        # When: 토큰 없이 게시글 삭제 요청
        response = self._post_delete(None, article_id)

        # Then: 권한 오류가 반환되어야 한다
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("_result", {}).get("status_code") == 403, body

    # 🔒 Boundary - 학습자 토큰으로 게시글 삭제 API 호출
    def test_board_article_delete_boundary(self):
        # Given: 학습자 토큰과 유효한 board_article_id가 있을 때
        article_id = os.getenv("BOARD_ARTICLE_ID_BOUNDARY")
        assert article_id, "BOARD_ARTICLE_ID_BOUNDARY is required in .env"

        # When: 학습자 토큰으로 게시글 삭제 요청
        response = self._post_delete(os.getenv("LEARNER_TOKEN"), article_id)

        # Then: 권한 오류가 반환되어야 한다
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("_result", {}).get("status_code") == 403, body