# -*- coding: utf-8 -*-
import pytest
import requests
# pytest tests/article/test_article.py -v 
# ===== 환경 설정 =====
BASE_URL_CLASSROOM = "https://api-classroom.elice.io"
BASE_URL_REST = "https://api-rest.elice.io"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjg5MDczODcsIm5vbmNlIjoiOWd5bW9CYWJja0NxZU13bSIsImlhdCI6MTc3NTIxNzQwMiwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.RqB3zVgu_5MyTkhrig5S04GW6HR-eJxDrc7O2EDH9h4"
ORG = "qatrack"
CLASSROOM_ID = "11968486-1a7b-4105-8ae3-b397ea4f54a7"
BOARD_ID = 9565
MY_ARTICLE_ID = 75085       # 본인이 작성한 게시글
OTHER_ARTICLE_ID = 69780    # 다른 사람이 작성한 게시글 ([매니저]장은서)

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

class TestArticlePositive:

    def test_유효한_토큰으로_게시글_목록_조회(self):
        """
        [요청 조건] 유효한 토큰 + classroom_id + skip=0 + count=10
        [예상 결과] 200 OK, 게시글 목록 정상 반환
        """
        response = requests.get(
            f"{BASE_URL_CLASSROOM}/classroom/{CLASSROOM_ID}/article",
            headers=HEADERS_WITH_TOKEN,
            params={"skip": 0, "count": 10},
        )

        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert isinstance(data, list), (
            f"응답이 리스트 형태가 아님: {data}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestArticleNegative:

    def test_토큰_없이_GET_요청(self):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 403 Forbidden, 인증 에러 반환
        [실제 결과] 403 Forbidden, no_access_token
        """
        response = requests.get(
            f"{BASE_URL_CLASSROOM}/classroom/{CLASSROOM_ID}/article",
            headers=HEADERS_NO_TOKEN,
            params={"skip": 0, "count": 10},
        )

        assert response.status_code == 403, (
            f"예상: 403, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("code") == "no_access_token", (
            f"에러 코드 불일치: {data}"
        )

    def test_skip_누락(self):
        """
        [요청 조건] skip 누락
        [예상 결과] 422 Unprocessable Entity, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, skip Field required
        """
        response = requests.get(
            f"{BASE_URL_CLASSROOM}/classroom/{CLASSROOM_ID}/article",
            headers=HEADERS_WITH_TOKEN,
            params={"count": 10},
        )

        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "skip"
            for err in data.get("detail", [])
        ), f"skip 누락 에러 미확인: {data}"

    def test_count_누락(self):
        """
        [요청 조건] count 누락
        [예상 결과] 422 Unprocessable Entity, 필수값 누락 에러 반환
        [실제 결과] 422 Unprocessable Entity, count Field required
        """
        response = requests.get(
            f"{BASE_URL_CLASSROOM}/classroom/{CLASSROOM_ID}/article",
            headers=HEADERS_WITH_TOKEN,
            params={"skip": 0},
        )

        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("loc", [])[-1] == "count"
            for err in data.get("detail", [])
        ), f"count 누락 에러 미확인: {data}"

    def test_count에_문자열_전달(self):
        """
        [요청 조건] count = abc (문자열 전달, int 필요)
        [예상 결과] 400 Bad Request, 타입 에러 반환
        [실제 결과] 422 Unprocessable Entity, int_parsing
        """
        response = requests.get(
            f"{BASE_URL_CLASSROOM}/classroom/{CLASSROOM_ID}/article",
            headers=HEADERS_WITH_TOKEN,
            params={"skip": 0, "count": "abc"},
        )

        assert response.status_code == 422, (
            f"예상: 422, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert any(
            err.get("type") == "int_parsing"
            for err in data.get("detail", [])
        ), f"int_parsing 에러 미확인: {data}"

    def test_존재하지_않는_classroom_id로_요청(self):
        """
        [요청 조건] 존재하지 않는 classroom_id로 요청
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] 409 Conflict, model_not_found
        """
        response = requests.get(
            f"{BASE_URL_CLASSROOM}/classroom/00000000-0000-0000-0000-000000000000/article",
            headers=HEADERS_WITH_TOKEN,
            params={"skip": 0, "count": 10},
        )

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

    def test_다른_사람_게시글_수정_시도(self):
        """
        [요청 조건] 학습자 토큰으로 다른 사람 게시글 수정 시도
        [예상 결과] 403 Forbidden, 권한 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, resource_not_found
                   (본인 글이 아니면 리소스 자체를 찾을 수 없음으로 처리)
        [Pass/Fail] Pass
        """
        response = requests.post(
            f"{BASE_URL_REST}/org/{ORG}/board/article/edit/",
            headers=HEADERS_WITH_TOKEN,
            data={
                "board_article_id": OTHER_ARTICLE_ID,
                "board_id": BOARD_ID,
                "title": "수정 테스트",
                "content": "수정 내용",
                "is_secret": "false",
            },
        )

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