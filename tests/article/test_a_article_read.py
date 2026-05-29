# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/article/test_a_article_read.py -v

load_dotenv()

# ===== 환경 설정 =====
VALID_ARTICLE_ID = int(os.getenv("VALID_ARTICLE_ID", "75044"))  # [코치]이상엽 작성 게시글
ORG = os.getenv("ORG", "qatrack")


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestArticleReadPositive:

    def test_article_read_positive(self, learner_rest_client):
        """
        [요청 조건] 유효한 토큰 + 유효한 board_article_id
        [예상 결과] 200 OK, 게시글 상세 정보 반환
        [실제 결과] 200 OK, board_article 데이터 정상 반환
        """
        # Given: 유효한 학습자 토큰과 유효한 board_article_id가 있을 때
        params = {"board_article_id": VALID_ARTICLE_ID}

        # When: 게시글 단건 조회 API 호출
        response = learner_rest_client.get(
            f"/org/{ORG}/board/article/get/",
            params=params,
        )

        # Then: 200 OK와 게시글 상세 정보가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "ok", (
            f"응답 status 불일치: {data}"
        )
        article = data.get("board_article", {})
        assert article.get("id") == VALID_ARTICLE_ID, (
            f"게시글 ID 불일치: {data}"
        )
        assert article.get("title") is not None, (
            f"title 필드 없음: {data}"
        )
        assert article.get("content") is not None, (
            f"content 필드 없음: {data}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestArticleReadNegative:

    def test_article_read_without_token(self, learner_rest_client):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 401 Unauthorized, 인증 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 403, not_found_sessionkey
        """
        # Given: 토큰이 없는 상태일 때
        params = {"board_article_id": VALID_ARTICLE_ID}

        # When: 토큰 없이 게시글 단건 조회 API 호출
        response = learner_rest_client.get_no_token(
            f"/org/{ORG}/board/article/get/",
            params=params,
        )

        # Then: 인증 에러가 반환되어야 한다
        # 이 서버는 HTTP 200 + Body에 실제 에러코드 반환하는 방식
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "fail", (
            f"응답 status 불일치: {data}"
        )
        assert data.get("_result", {}).get("status_code") == 403, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "not_found_sessionkey", (
            f"에러 코드 불일치: {data}"
        )

    def test_article_read_missing_article_id(self, learner_rest_client):
        """
        [요청 조건] board_article_id 누락
        [예상 결과] 400 Bad Request, 필수값 누락 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (board_article_id required)
        """
        # Given: board_article_id가 없는 상태일 때

        # When: board_article_id 없이 게시글 단건 조회 API 호출
        response = learner_rest_client.get(
            f"/org/{ORG}/board/article/get/",
        )

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "fail", (
            f"응답 status 불일치: {data}"
        )
        assert data.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {data}"
        )
        assert data.get("fail_detail", {}).get("invalid_params", {}).get("board_article_id") == "required", (
            f"board_article_id required 에러 미확인: {data}"
        )

    def test_article_read_invalid_article_id_type(self, learner_rest_client):
        """
        [요청 조건] board_article_id에 문자열(abc) 전달
        [예상 결과] 400 Bad Request, 타입 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter
        """
        # Given: board_article_id에 잘못된 타입(문자열)이 있을 때
        params = {"board_article_id": "abc"}

        # When: 잘못된 타입의 board_article_id로 게시글 단건 조회 API 호출
        response = learner_rest_client.get(
            f"/org/{ORG}/board/article/get/",
            params=params,
        )

        # Then: 타입 에러가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "fail", (
            f"응답 status 불일치: {data}"
        )
        assert data.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {data}"
        )