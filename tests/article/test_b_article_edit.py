# -*- coding: utf-8 -*-
import pytest
import os
import requests as req
from dotenv import load_dotenv
# pytest tests/article/test_b_article_edit.py -v

load_dotenv()

# ===== 환경 설정 =====
ORG = "qaproject"
EDUCATOR_CLASSROOM_ID = os.getenv("EDUCATOR_CLASSROOM_ID")
LEARNER_CLASSROOM_ID = os.getenv("LEARNER_CLASSROOM_ID")
OTHER_ARTICLE_ID = 75252  # 다른 사람이 작성한 게시글


# ===== Fixture: 테스트용 게시글 자동 생성 =====
@pytest.fixture
def board_article_id(educator_rest_client):
    """테스트용 게시글을 생성하고 board_article_id 반환"""
    data = {
        "classroom_id": EDUCATOR_CLASSROOM_ID,
        "title": "수정 테스트용 게시글",
        "content": "수정 테스트용 내용",
        "is_secret": "false",
    }
    response = educator_rest_client.post_form(
        f"/org/{ORG}/board/article/edit/",
        data=data,
    )
    assert response.status_code == 200, f"게시글 생성 실패: {response.text}"
    return response.json().get("board_article_id")


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestBoardArticleEditPositive:

    def test_board_article_create_positive(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + 유효한 classroom_id + title + content + is_secret
        [예상 결과] 200 OK, 게시글 정상 생성 및 board_article_id 반환
        [실제 결과] 200 OK, 게시글 정상 생성 (board_article_id: 75271)
        """
        # Given: 교육자 토큰과 유효한 게시글 데이터가 있을 때
        data = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "title": "교육자 공지 테스트",
            "content": "교육자 공지 내용",
            "is_secret": "false",
        }

        # When: 게시글 작성 API 호출
        response = educator_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=data,
        )

        # Then: 200 OK와 board_article_id가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        result = response.json()
        assert result.get("_result", {}).get("status") == "ok", (
            f"응답 status 불일치: {result}"
        )
        assert "board_article_id" in result, (
            f"board_article_id 없음: {result}"
        )

    def test_board_article_update_positive(self, educator_rest_client, board_article_id):
        """
        [요청 조건] 교육자 토큰 + 유효한 board_article_id + classroom_id + 수정할 title + content + is_secret
        [예상 결과] 200 OK, 게시글 정상 수정 및 board_article_id 반환
        [실제 결과] 200 OK, 게시글 정상 수정 (board_article_id: 75271)
        """
        # Given: 교육자 토큰과 수정할 게시글 데이터가 있을 때
        data = {
            "board_article_id": board_article_id,
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "title": "교육자 공지 테스트 수정됨",
            "content": "교육자 공지 내용 수정됨",
            "is_secret": "false",
        }

        # When: 게시글 수정 API 호출
        response = educator_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=data,
        )

        # Then: 200 OK와 board_article_id가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        result = response.json()
        assert result.get("_result", {}).get("status") == "ok", (
            f"응답 status 불일치: {result}"
        )
        assert result.get("board_article_id") == board_article_id, (
            f"board_article_id 불일치: {result}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestBoardArticleEditNegative:

    def test_board_article_edit_missing_title(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + classroom_id + content + is_secret (title 누락)
        [예상 결과] 400 Bad Request, 필수값 누락 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (title required)
        """
        # Given: title이 없는 게시글 데이터가 있을 때
        data = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "content": "교육자 공지 내용",
            "is_secret": "false",
        }

        # When: title 없이 게시글 작성 API 호출
        response = educator_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=data,
        )

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        result = response.json()
        assert result.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {result}"
        )
        assert result.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {result}"
        )

    def test_board_article_edit_missing_content(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + classroom_id + title + is_secret (content 누락)
        [예상 결과] 400 Bad Request, 필수값 누락 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (content required)
        """
        # Given: content가 없는 게시글 데이터가 있을 때
        data = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "title": "교육자 공지 테스트",
            "is_secret": "false",
        }

        # When: content 없이 게시글 작성 API 호출
        response = educator_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=data,
        )

        # Then: 필수값 누락 에러가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        result = response.json()
        assert result.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {result}"
        )
        assert result.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {result}"
        )

    def test_board_article_edit_title_too_long(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + classroom_id + 129자 title + content + is_secret
        [예상 결과] 400 Bad Request, 유효성 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter (title: should be between 1 and 128 letters/elements)
        """
        # Given: title이 129자인 게시글 데이터가 있을 때
        data = {
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "title": "아" * 129,
            "content": "교육자 공지 내용",
            "is_secret": "false",
        }

        # When: 129자 title로 게시글 작성 API 호출
        response = educator_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=data,
        )

        # Then: 유효성 에러가 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        result = response.json()
        assert result.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {result}"
        )
        assert result.get("fail_code") == "invalid_parameter", (
            f"에러 코드 불일치: {result}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestBoardArticleEditBoundary:

    def test_board_article_edit_other_user(self, educator_rest_client):
        """
        [요청 조건] 교육자 토큰 + 다른 사람이 작성한 board_article_id로 수정 시도
        [예상 결과] 403 Forbidden, 권한 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, resource_not_found
                   (본인 글이 아니면 리소스 자체를 찾을 수 없음으로 처리)
        """
        # Given: 다른 사람이 작성한 게시글 ID가 있을 때
        data = {
            "board_article_id": OTHER_ARTICLE_ID,
            "classroom_id": EDUCATOR_CLASSROOM_ID,
            "title": "수정 테스트",
            "content": "수정 내용",
            "is_secret": "false",
        }

        # When: 다른 사람 게시글 수정 API 호출
        response = educator_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=data,
        )

        # Then: 리소스 없음 에러가 반환되어야 한다 (권한 없는 게시글 수정 불가)
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        result = response.json()
        assert result.get("_result", {}).get("status") == "fail", (
            f"다른 사람 게시글 수정 가능 상태 — 권한 이슈\n{result}"
        )
        assert result.get("fail_code") == "resource_not_found", (
            f"에러 코드 불일치: {result}"
        )