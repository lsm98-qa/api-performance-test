import pytest
import os
from dotenv import load_dotenv
from utils.api_client import APIClient

load_dotenv()

# ===========================
# 학습자 API 클라이언트 (Classroom)
# ===========================
@pytest.fixture
def learner_client():
    """학습자 토큰으로 API 호출하는 클라이언트 (BASE_URL_CLASSROOM)"""
    return APIClient(
        token=os.getenv("LEARNER_TOKEN"),
        base_url=os.getenv("BASE_URL_CLASSROOM")
    )

# ===========================
# 학습자 API 클라이언트 (REST)
# ===========================
@pytest.fixture
def learner_rest_client():
    """학습자 토큰으로 API 호출하는 클라이언트 (BASE_URL_REST)"""
    return APIClient(
        token=os.getenv("LEARNER_TOKEN"),
        base_url=os.getenv("BASE_URL_REST")
    )

# ===========================
# 교육자 API 클라이언트
# ===========================
@pytest.fixture
def educator_client():
    """교육자 토큰으로 API 호출하는 클라이언트"""
    return APIClient(
        token=os.getenv("EDUCATOR_TOKEN"),
        base_url=os.getenv("BASE_URL_CLASSROOM")
    )

# ===========================
# 공통 변수
# ===========================
@pytest.fixture
def classroom_id():
    return os.getenv("CLASSROOM_ID")

@pytest.fixture
def account_id():
    return os.getenv("ACCOUNT_ID")