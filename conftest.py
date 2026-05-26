import os
import pytest
from dotenv import load_dotenv
from utils.api_client import APIClient

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    assert value, f"필수 환경변수 누락: {name}"
    return value


# ===========================
# 학습자 API 클라이언트 (Classroom)
# ===========================
@pytest.fixture
def learner_client():
    """학습자 토큰으로 API 호출하는 클라이언트 (BASE_URL_CLASSROOM)"""
    return APIClient(
        token=_require_env("LEARNER_TOKEN"),
        base_url=_require_env("BASE_URL_CLASSROOM"),
    )


# ===========================
# 학습자 API 클라이언트 (REST)
# ===========================
@pytest.fixture
def learner_rest_client():
    """학습자 토큰으로 API 호출하는 클라이언트 (BASE_URL_REST)"""
    return APIClient(
        token=_require_env("LEARNER_TOKEN"),
        base_url=_require_env("BASE_URL_REST"),
    )


# ===========================
# 교육자 API 클라이언트 (Classroom)
# ===========================
@pytest.fixture
def educator_client():
    """교육자 토큰으로 API 호출하는 클라이언트 (BASE_URL_CLASSROOM)"""
    return APIClient(
        token=_require_env("EDUCATOR_TOKEN"),
        base_url=_require_env("BASE_URL_CLASSROOM"),
    )


# ===========================
# 교육자 API 클라이언트 (REST)
# ===========================
@pytest.fixture
def educator_rest_client():
    """교육자 토큰으로 API 호출하는 클라이언트 (BASE_URL_REST)"""
    return APIClient(
        token=_require_env("EDUCATOR_TOKEN"),
        base_url=_require_env("BASE_URL_REST"),
    )


# ===========================
# 공통 변수
# ===========================
@pytest.fixture
def classroom_id():
    return _require_env("CLASSROOM_ID")


@pytest.fixture
def account_id():
    return _require_env("ACCOUNT_ID")


# ===========================
# 교육자 스케줄 fixture
# ===========================
@pytest.fixture
def educator_schedule_id(educator_client):
    """교육자 테스트용 스케줄을 생성하고 테스트 후 자동 삭제"""
    educator_classroom_id = _require_env("EDUCATOR_CLASSROOM_ID")

    body = {
        "classroom_id": educator_classroom_id,
        "summary": "테스트용 수업",
        "dt_start": "2026-09-01T09:00:00.000Z",
        "dt_end": "2026-09-01T10:00:00.000Z",
    }
    response = educator_client.post("/schedule", data=body)
    assert response.status_code == 200, f"스케줄 생성 실패: {response.text}"

    list_response = educator_client.get(
        "/schedule",
        params={
            "classroom_id": educator_classroom_id,
            "dt_start_ge": "2026-09-01T00:00:00.000Z",
            "dt_start_le": "2026-09-01T23:59:59.999Z",
            "count": 20,
        },
    )
    assert list_response.status_code == 200, f"스케줄 조회 실패: {list_response.text}"

    schedules = list_response.json()
    target = next((s for s in schedules if s.get("summary") == "테스트용 수업"), None)
    assert target is not None, "생성된 스케줄을 찾을 수 없음"
    schedule_id = target["id"]

    yield schedule_id

    educator_client.delete(
        f"/schedule/{schedule_id}",
        data={"classroom_id": educator_classroom_id},
    )