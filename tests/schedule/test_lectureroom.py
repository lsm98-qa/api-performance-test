# -*- coding: utf-8 -*-
import pytest
import requests
# pytest tests/schedule/test_lectureroom.py -v 
# ===== 환경 설정 =====
BASE_URL = "https://api-rest.elice.io"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjg5MDczODcsIm5vbmNlIjoiOWd5bW9CYWJja0NxZU13bSIsImlhdCI6MTc3NTIxNzQwMiwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.RqB3zVgu_5MyTkhrig5S04GW6HR-eJxDrc7O2EDH9h4"
ORG = "qatrack"
VALID_LECTUREROOM_ID = 142899       # [1팀🩶] 강의실 (is_participating_as_student: true)
INVALID_LECTUREROOM_ID = 143638     # [코치님 강의실] (is_participating_as_student: false)

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

class TestLectureroomPositive:

    def test_정상_학습자_토큰으로_강의실_입장_정보_조회(self):
        """
        [요청 조건] 학습자 토큰 + 유효한 org + 유효한 lectureroom_id
        [예상 결과] 200 OK, 강의실 입장 가능 상태로 정보 반환
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/course/lectureroom/get/",
            headers=HEADERS_WITH_TOKEN,
            params={"lectureroom_id": VALID_LECTUREROOM_ID},
        )

        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status") == "ok", (
            f"응답 status 불일치: {data}"
        )


# ===================================================
# ❌ Negative (비정상)
# ===================================================

class TestLectureroomNegative:
 
    def test_토큰_없이_GET_요청(self):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 401 Unauthorized, 인증 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 403, not_found_sessionkey
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/course/lectureroom/get/",
            headers=HEADERS_NO_TOKEN,
            params={"lectureroom_id": VALID_LECTUREROOM_ID},
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

    def test_lectureroom_id에_문자열_전달(self):
        """
        [요청 조건] lectureroom_id에 문자열(abc) 잘못된 타입 전달
        [예상 결과] 400 Bad Request, 타입 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/course/lectureroom/get/",
            headers=HEADERS_WITH_TOKEN,
            params={"lectureroom_id": "abc"},
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

    def test_존재하지_않는_lectureroom_id로_요청(self):
        """
        [요청 조건] 존재하지 않는 lectureroom_id로 요청
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, resource_not_found
        """
        response = requests.get(
            f"{BASE_URL}/org/{ORG}/course/lectureroom/get/",
            headers=HEADERS_WITH_TOKEN,
            params={"lectureroom_id": 99999999},
        )

        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status_code") == 400, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "resource_not_found", (
            f"에러 코드 불일치: {data}"
        )


# ===================================================
# 🔒 Boundary (권한)
# ===================================================

class TestLectureroomBoundary:
 
    def test_학습자_토큰으로_교육자_역할_입장_시도(self):
        """
        [요청 조건] 학습자 토큰으로 role=10(교육자)으로 강의실 입장 시도
        [예상 결과] 403 Forbidden, 권한 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 409, insufficient_permission
                   (TA 이상만 교육자 역할 가능)
        [Pass/Fail] Pass
        """
        response = requests.post(
            f"{BASE_URL}/org/{ORG}/course/lectureroom/join/",
            headers=HEADERS_WITH_TOKEN,
            data={
                "lectureroom_id": VALID_LECTUREROOM_ID,
                "role": 10,
            },
        )
 
        assert response.status_code == 200, (
            f"예상: 200, 실제: {response.status_code}\n{response.text}"
        )
        data = response.json()
        assert data.get("_result", {}).get("status_code") == 409, (
            f"Body status_code 불일치: {data}"
        )
        assert data.get("fail_code") == "insufficient_permission", (
            f"에러 코드 불일치: {data}"
        )