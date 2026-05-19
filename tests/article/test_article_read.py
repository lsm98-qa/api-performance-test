# -*- coding: utf-8 -*-
import pytest
import requests
# pytest tests/article/test_article_read.py -v 
# ===== 환경 설정 =====
BASE_URL = "https://api-rest.elice.io"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjg5MDczODcsIm5vbmNlIjoiOWd5bW9CYWJja0NxZU13bSIsImlhdCI6MTc3NTIxNzQwMiwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.RqB3zVgu_5MyTkhrig5S04GW6HR-eJxDrc7O2EDH9h4"
ORG = "qatrack"
VALID_ARTICLE_ID = 75044    # [코치]이상엽 작성 게시글

HEADERS_WITH_TOKEN = {
    "Authorization": f"Bearer {VALID_TOKEN}",
    "x-elice-org-name-short": ORG,
}

HEADERS_NO_TOKEN = {
    "x-elice-org-name-short": ORG,
}


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestArticleReadPositive:

    def test_유효한_토큰으로_게시글_단건_조회(self):
        """
        [요청 조건] 유효한 토큰 + 유효한 board_article_id
        [예상 결과] 200 OK, 게시글 상세 정보 반환
        [실제 결과] 200 OK, board_article 데이터 정상 반환
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/board/article/get/",
            headers=HEADERS_WITH_TOKEN,
            params={"board_article_id": VALID_ARTICLE_ID},
        )

        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "ok", (
            f"응답 status 불일치: {data}"
        )
        assert data.get("board_article", {}).get("id") == VALID_ARTICLE_ID, (
            f"게시글 ID 불일치: {data}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestArticleReadNegative:

    def test_토큰_없이_GET_요청(self):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 401 Unauthorized, 인증 에러 반환
        [실제 결과] 403 Forbidden (신원은 확인됐지만 접근 거부)
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/board/article/get/",
            headers=HEADERS_NO_TOKEN,
            params={"board_article_id": VALID_ARTICLE_ID},
        )

        # 이 서버는 HTTP 200 + Body에 실제 에러코드 반환하는 방식
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status_code") == 403, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "not_found_sessionkey", (
            f"에러 코드 불일치: {data}"
        )

    def test_board_article_id_누락(self):
        """
        [요청 조건] board_article_id 누락
        [예상 결과] 400 Bad Request, 필수값 누락 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (board_article_id required)
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/board/article/get/",
            headers=HEADERS_WITH_TOKEN,
        )

        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {data}"
        )
        assert data.get("fail_detail", {}).get("invalid_params", {}).get("board_article_id") == "required", (
            f"board_article_id required 에러 미확인: {data}"
        )

    def test_board_article_id에_문자열_전달(self):
        """
        [요청 조건] board_article_id에 문자열(abc) 전달
        [예상 결과] 400 Bad Request, 타입 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (board_article_id required)
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/board/article/get/",
            headers=HEADERS_WITH_TOKEN,
            params={"board_article_id": "abc"},
        )

        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {data}"
        )