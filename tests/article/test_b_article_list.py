# -*- coding: utf-8 -*-
import pytest
import os
import requests as req
from dotenv import load_dotenv
# pytest tests/article/test_b_article_list.py -v

load_dotenv()

# ===== 환경 설정 =====
ORG = os.getenv("EDUCATOR_ORG", "qaproject")
BOARD_ID = int(os.getenv("EDUCATOR_BOARD_ID", "10193"))


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestBoardArticleListPositive:

    def test_board_article_list_positive(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + 유효한 board_id + offset=0 + count=10
        [예상 결과] 200 OK, 게시글 목록 정상 반환
        [실제 결과] 200 OK, 게시글 목록 정상 반환
        """
        # Given: 교육자 토큰과 유효한 board_id가 있을 때
        params = {
            "board_id": BOARD_ID,
            "offset": 0,
            "count": 10,
        }

        # When: 게시판 목록 조회 API 호출
        response = educator_rest_client.get(
            f"/org/{ORG}/board/article/list/",
            params=params,
        )

        # Then: 200 OK와 게시글 목록이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "ok", (
            f"응답 status 불일치: {data}"
        )
        assert "board_articles" in data, (
            f"board_articles 필드 없음: {data}"
        )
        assert isinstance(data.get("board_article_count"), int), (
            f"board_article_count 필드 없음: {data}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestBoardArticleListNegative:

    def test_board_article_list_missing_board_id(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + board_id 누락 + offset=0 + count=10
        [예상 결과] 400 Bad Request, 필수값 누락 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (board_id required)
        """
        # Given: board_id가 없는 상태일 때
        params = {
            "offset": 0,
            "count": 10,
        }

        # When: board_id 없이 게시판 목록 조회 API 호출
        response = educator_rest_client.get(
            f"/org/{ORG}/board/article/list/",
            params=params,
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
        assert data.get("fail_detail", {}).get("invalid_params", {}).get("board_id") == "required", (
            f"board_id required 에러 미확인: {data}"
        )

    def test_board_article_list_count_over_limit(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + 유효한 board_id + count=21 (최대 20 초과)
        [예상 결과] 400 Bad Request, 유효성 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (count: should be between 1 and 20)
        """
        # Given: count가 최대값(20)을 초과한 상태일 때
        params = {
            "board_id": BOARD_ID,
            "offset": 0,
            "count": 21,
        }

        # When: count=21로 게시판 목록 조회 API 호출
        response = educator_rest_client.get(
            f"/org/{ORG}/board/article/list/",
            params=params,
        )

        # Then: 유효성 에러가 반환되어야 한다
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


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestBoardArticleListBoundary:

    def test_board_article_list_different_org(self, educator_rest_client):
        """
        [요청 조건] qaproject 토큰 + qatrack org로 게시판 목록 조회 시도
        [예상 결과] 403 Forbidden, 기관 간 접근 차단
        [실제 결과] HTTP 200 / Body status_code: 409, insufficient_permission
        """
        # Given: 다른 기관 헤더로 게시판 목록 조회 시도
        headers = {
            **educator_rest_client.headers,
            "x-elice-org-name-short": "qatrack",
        }
        params = {
            "board_id": BOARD_ID,
            "offset": 0,
            "count": 10,
        }

        # When: 다른 기관 org로 게시판 목록 조회 API 호출
        response = req.get(
            f"{educator_rest_client.base_url}/org/qatrack/board/article/list/",
            headers=headers,
            params=params,
            timeout=10,
        )

        # Then: 기관 간 접근 차단 에러가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "fail", (
            f"응답 status 불일치: {data}"
        )
        assert data.get("_result", {}).get("status_code") == 409, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "insufficient_permission", (
            f"에러 코드 불일치: {data}"
        )