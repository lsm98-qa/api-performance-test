import requests
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    """
    API Request Wrapper
    - 토큰 자동 포함
    - Base URL 자동 설정
    - 공통 헤더 관리
    """

    def __init__(self, token: str = None, base_url: str = None):
        self.base_url = base_url or os.getenv("BASE_URL_CLASSROOM")
        self.token = token or os.getenv("LEARNER_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str, params: dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return requests.get(url, headers=self.headers, params=params)

    def post(self, endpoint: str, data: dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return requests.post(url, headers=self.headers, json=data)

    def patch(self, endpoint: str, data: dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return requests.patch(url, headers=self.headers, json=data)

    def delete(self, endpoint: str) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return requests.delete(url, headers=self.headers)

    def get_no_token(self, endpoint: str, params: dict = None) -> requests.Response:
        """토큰 없이 요청 (Negative 테스트용)"""
        url = f"{self.base_url}{endpoint}"
        return requests.get(url, params=params)

    def get_invalid_token(self, endpoint: str, params: dict = None) -> requests.Response:
        """잘못된 토큰으로 요청 (Negative 테스트용)"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": "Bearer invalid_token_1234"}
        return requests.get(url, headers=headers, params=params)
