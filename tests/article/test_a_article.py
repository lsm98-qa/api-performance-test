# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/article/test_a_article.py -v

load_dotenv()

# ===== 환경 설정 =====
ORG = os.getenv("ORG", "qatrack")
BOARD_ID = int(os.getenv("BOARD_ID", "9565"))
MY_ARTICLE_ID = int(os.getenv("MY_ARTICLE_ID", "75085"))        # 본인이 작성한 게시글
OTHER_ARTICLE_ID = int(os.getenv("OTHER_ARTICLE_ID", "69780"))  # 다른 사람이 작성한 게시글 ([매니저]장은서)


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestArticlePositive:

    def test_article_list_positive(self, learner_client, classroom_id):
        """
        [요청 조건] 유효한 토큰 + classroom_id + skip=0 + count=10
        [예상 결과] 200 OK, 게시글 목록 정상 반환
        """
        # Given: 유효한 학습자 토큰과 classroom_id가 있을 때
        params = {"skip": 0, "count": 10}

        # When: 게시글 목록 조회 API 호출
        response = learner_client.get(
            f"/classroom/{classroom_id}/article",
            params=params,
        )

        # Then: 200 OK와 게시글 목록이 반환되어야 한다
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert isinstance(data, list), (
            f"응답이 리스트 형태가 아님: {data}"
        )
        if len(data) > 0:
            article = data[0]
            assert "id" in article, f"id 필드 없음: {article}"
            assert "title" in article, f"title 필드 없음: {article}"
            assert "user" in article, f"user 필드 없음: {article}"


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestArticleNegative:

    def test_article_list_without_token(self, learner_client, classroom_id):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 403 Forbidden, 인증 에러 반환
        [실제 결과] 403 Forbidden, no_access_token
        """
        # Given: 토큰이 없는 상태일 때
        params = {"skip": 0, "count": 10}

        # When: 토큰 없이 게시글 목록 조회 API 호출
        response = learner_client.get_no_token(
            f"/classroom/{classroom_id}/article",
            params=params,
        )

        # Then: 403 Forbidden 인증 에러가 반환되어야 한다
        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "no_access_token", (
            f"에러 코드 불일치: {data}"
        )

    def test_article_list_missing_skip(self, learner_client, classroom_id):
        """
        [요청 조건] skip 누락
        [예상 결과] 422 Unprocessable Entity, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, skip Field required
        """
        # Given: skip 파라미터가 없는 상태일 때
        params = {"count": 10}

        # When: skip 없이 게시글 목록 조회 API 호출
        response = learner_client.get(
            f"/classroom/{classroom_id}/article",
            params=params,
        )

        # Then: 422 Unprocessable Entity 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "skip"
            for err in data.get("detail", [])
        ), f"skip 누락 에러 미확인: {data}"

    def test_article_list_missing_count(self, learner_client, classroom_id):
        """
        [요청 조건] count 누락
        [예상 결과] 422 Unprocessable Entity, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, count Field required
        """
        # Given: count 파라미터가 없는 상태일 때
        params = {"skip": 0}

        # When: count 없이 게시글 목록 조회 API 호출
        response = learner_client.get(
            f"/classroom/{classroom_id}/article",
            params=params,
        )

        # Then: 422 Unprocessable Entity 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "count"
            for err in data.get("detail", [])
        ), f"count 누락 에러 미확인: {data}"

    def test_article_list_invalid_count_type(self, learner_client, classroom_id):
        """
        [요청 조건] count = abc (문자열 전달, int 필요)
        [예상 결과] 400 Bad Request, 타입 에러 반환
        [실제 결과] 422 Unprocessable Entity, int_parsing
        """
        # Given: count에 잘못된 타입(문자열)이 있을 때
        params = {"skip": 0, "count": "abc"}

        # When: 잘못된 타입의 count로 게시글 목록 조회 API 호출
        response = learner_client.get(
            f"/classroom/{classroom_id}/article",
            params=params,
        )

        # Then: 422 Unprocessable Entity 타입 에러가 반환되어야 한다
        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("type") == "int_parsing"
            for err in data.get("detail", [])
        ), f"int_parsing 에러 미확인: {data}"

    def test_article_list_invalid_classroom_id(self, learner_client):
        """
        [요청 조건] 존재하지 않는 classroom_id로 요청
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] 409 Conflict, model_not_found
        """
        # Given: 존재하지 않는 classroom_id가 있을 때
        params = {"skip": 0, "count": 10}

        # When: 존재하지 않는 classroom_id로 게시글 목록 조회 API 호출
        response = learner_client.get(
            "/classroom/00000000-0000-0000-0000-000000000000/article",
            params=params,
        )

        # Then: 리소스 없음 에러가 반환되어야 한다
        assert response.status_code == 409, (
            f"예상: 409, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "model_not_found", (
            f"에러 코드 불일치: {data}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestArticleBoundary:

    def test_article_edit_other_user(self, learner_rest_client):
        """
        [요청 조건] 학습자 토큰으로 다른 사람 게시글 수정 시도
        [예상 결과] 403 Forbidden, 권한 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, resource_not_found
                   (본인 글이 아니면 리소스 자체를 찾을 수 없음으로 처리)
        """
        # Given: 학습자 토큰과 다른 사람의 게시글 ID가 있을 때
        form_data = {
            "board_article_id": OTHER_ARTICLE_ID,
            "board_id": BOARD_ID,
            "title": "수정 테스트",
            "content": "수정 내용",
            "is_secret": "false",
        }

        # When: 다른 사람 게시글 수정 API 호출
        response = learner_rest_client.post_form(
            f"/org/{ORG}/board/article/edit/",
            data=form_data,
        )

        # Then: 리소스 없음 에러가 반환되어야 한다 (권한 없는 게시글 수정 불가)
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "fail", (
            f"다른 사람 게시글 수정 가능 상태 — 권한 이슈\n{data}"
        )
        assert data.get("fail_code") == "resource_not_found", (
            f"에러 코드 불일치: {data}"
        )