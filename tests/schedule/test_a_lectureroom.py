# -*- coding: utf-8 -*-
import pytest
import os
from dotenv import load_dotenv
# pytest tests/schedule/test_a_lectureroom.py -v

load_dotenv()

# ===== 환경 설정 =====
ORG = os.getenv("ORG", "qatrack")
VALID_LECTUREROOM_ID = 142899       # [1팀🩶] 강의실 (is_participating_as_student: true)
INVALID_LECTUREROOM_ID = 143638     # [코치님 강의실] (is_participating_as_student: false)


# ===================================================
# ✅ Positive (정상)
# ===================================================

class TestLectureroomPositive:

    def test_lectureroom_get_positive(self, learner_rest_client):
        """
        [요청 조건] 학습자 토큰 + 유효한 org + 유효한 lectureroom_id
        [예상 결과] 200 OK, 강의실 입장 가능 상태로 정보 반환
        """
        # Given: 유효한 학습자 토큰과 lectureroom_id가 있을 때
        params = {"lectureroom_id": VALID_LECTUREROOM_ID}

        # When: 강의실 입장 정보 조회 API 호출
        response = learner_rest_client.get(
            f"/org/{ORG}/course/lectureroom/get/",
            params=params,
        )

        # Then: 200 OK와 강의실 입장 정보가 반환되어야 한다
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

    def test_lectureroom_get_without_token(self, learner_rest_client):
        """
        [요청 조건] 토큰 없이 GET 요청
        [예상 결과] 401 Unauthorized, 인증 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 403, not_found_sessionkey
        """
        # Given: 토큰이 없는 상태일 때
        params = {"lectureroom_id": VALID_LECTUREROOM_ID}

        # When: 토큰 없이 강의실 입장 정보 조회 API 호출
        response = learner_rest_client.get_no_token(
            f"/org/{ORG}/course/lectureroom/get/",
            params=params,
        )

        # Then: 인증 에러가 반환되어야 한다
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

    def test_lectureroom_get_invalid_id_type(self, learner_rest_client):
        """
        [요청 조건] lectureroom_id에 문자열(abc) 잘못된 타입 전달
        [예상 결과] 400 Bad Request, 타입 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, invalid_parameter
        """
        # Given: lectureroom_id에 잘못된 타입(문자열)이 있을 때
        params = {"lectureroom_id": "abc"}

        # When: 잘못된 타입의 lectureroom_id로 강의실 입장 정보 조회 API 호출
        response = learner_rest_client.get(
            f"/org/{ORG}/course/lectureroom/get/",
            params=params,
        )

        # Then: 타입 에러가 반환되어야 한다
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

    def test_lectureroom_get_invalid_id(self, learner_rest_client):
        """
        [요청 조건] 존재하지 않는 lectureroom_id로 요청
        [예상 결과] 404 Not Found, 리소스 없음 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 400, resource_not_found
        """
        # Given: 존재하지 않는 lectureroom_id가 있을 때
        params = {"lectureroom_id": 99999999}

        # When: 존재하지 않는 lectureroom_id로 강의실 입장 정보 조회 API 호출
        response = learner_rest_client.get(
            f"/org/{ORG}/course/lectureroom/get/",
            params=params,
        )

        # Then: 리소스 없음 에러가 반환되어야 한다
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

    def test_lectureroom_join_as_educator(self, learner_rest_client):
        """
        [요청 조건] 학습자 토큰으로 role=10(교육자)으로 강의실 입장 시도
        [예상 결과] 403 Forbidden, 권한 에러 반환
        [실제 결과] HTTP 200 / Body status_code: 409, insufficient_permission
                   (TA 이상만 교육자 역할 가능)
        """
        # Given: 학습자 토큰과 교육자 역할(role=10)이 있을 때
        data = {
            "lectureroom_id": VALID_LECTUREROOM_ID,
            "role": 10,
        }

        # When: 교육자 역할로 강의실 입장 API 호출
        response = learner_rest_client.post_form(
            f"/org/{ORG}/course/lectureroom/join/",
            data=data,
        )

        # Then: 권한 에러가 반환되어야 한다
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