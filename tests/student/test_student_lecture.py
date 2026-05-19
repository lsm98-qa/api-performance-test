import requests
 
URL = "https://api-dashboard.elice.io/student/8906962/lecture"
 
PARAMS = {
    "classroom_id": "11968486-1a7b-4105-8ae3-b397ea4f54a7",
    "course_id": 767828,
    "filter_lecture_id": 6652042,
    "offset": 0,
    "count": 1,
}
 
BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,ja;q=0.9,ko-KR;q=0.8,en-US;q=0.7,en;q=0.6",
    "origin": "https://qatrack.elice.io",
    "priority": "u=1, i",
    "referer": "https://qatrack.elice.io/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-elice-org-name-short": "qatrack",
}
 
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjg5MDY5NjIsIm5vbmNlIjoiN0hqdFh1SW9uaTFaODM2QyIsImlhdCI6MTc3Mzk2ODA5NCwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.1dIWoQNYnxatvI4fpPHHYMd3YzCouiNx6sz7tGv1hvU"
EXPIRED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjEyMzQ1Njc4LCJub25jZSI6ImV4cGlyZWROb25jZSIsImlhdCI6MTYwMDAwMDAwMCwiaXNzIjoiZWxpY2UtYWNjb3VudC1hcGkifQ.invalidsignature"
 
 
def send_request(headers: dict) -> requests.Response:
    return requests.get(URL, headers=headers, params=PARAMS, timeout=10)
 
 
def verify(test_name: str, response: requests.Response, expected_status: int):
    print(f"\n{'='*50}")
    print(f"테스트: {test_name}")
    print(f"Status Code : {response.status_code}")
 
    assert response.status_code == expected_status, (
        f"기대값 {expected_status} 이지만 실제값은 {response.status_code} 입니다."
    )
 
    print(f"✅ 검증 성공: {expected_status} 확인")
 
 
def run_tests():
    test_cases = [
        {
            "name": "유효한 토큰으로 GET 요청",
            "headers": {**BASE_HEADERS, "authorization": f"Bearer {VALID_TOKEN}"},
            "expected": 200,
        },
        {
            "name": "토큰 없이 GET 요청",
            "headers": BASE_HEADERS,
            "expected": 403,
        },
        {
            "name": "만료된 토큰으로 GET 요청",
            "headers": {**BASE_HEADERS, "authorization": f"Bearer {EXPIRED_TOKEN}"},
            "expected": 403,
        },
    ]
 
    results = {"pass": 0, "fail": 0}
 
    for case in test_cases:
        try:
            response = send_request(case["headers"])
            verify(case["name"], response, case["expected"])
            results["pass"] += 1
        except AssertionError as e:
            print(f"❌ 검증 실패: {e}")
            results["fail"] += 1
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 연결 오류: {e}")
            results["fail"] += 1
        except requests.exceptions.Timeout:
            print(f"❌ 요청 시간 초과")
            results["fail"] += 1
 
    print(f"\n{'='*50}")
    print(f"테스트 결과: {results['pass']}개 성공 / {results['fail']}개 실패")
 
 
if __name__ == "__main__":
    run_tests()