# 엘리스 LXP QA 프로젝트

## 📌 프로젝트 개요
엘리스 LXP 서비스의 **학습자/교육자 관점 API 기능 테스트 자동화** 프로젝트입니다.

- **Part 1**: API 기능 테스트 자동화 (pytest)
- **Part 2**: 부하 테스트 로그 분석 (JMeter)

---

## 📁 프로젝트 구조

```
qa_project/
├── conftest.py               # 공통 fixture (토큰, 클라이언트 설정)
├── .env                      # 환경변수 (토큰, URL 등) - GitLab 업로드 금지
├── .env.example              # 환경변수 예시
├── requirements.txt          # 패키지 목록
├── utils/
│   ├── __init__.py
│   └── api_client.py         # API Request Wrapper
└── tests/
    ├── __init__.py
    ├── test_classroom.py     # 클래스 홈 테스트
    ├── test_course.py        # 학습 과목 테스트
    ├── test_schedule.py      # 수업 일정 테스트
    └── test_board.py         # 게시판 테스트
```

---

## ⚙️ 환경 설정

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
cp .env.example .env

LEARNER_TOKEN=여기에_학습자_토큰_입력
EDUCATOR_TOKEN=여기에_교육자_토큰_입력
CLASSROOM_ID=여기에_클래스_ID_입력
```

### 3. 토큰 발급 방법
```
1. qatrack.elice.io 접속 후 로그인
2. F12 → Application → Cookies
3. eliceSessionKey 값 복사 → LEARNER_TOKEN에 입력
```

---

## 🧪 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 파일만 실행
pytest tests/test_classroom.py

# 결과 상세 출력
pytest -v
```

---

## 🛡️ Safety Design

### 동시성 통제
- 테스트는 순차 실행 (병렬 실행 옵션 비활성화)

### 호출 빈도 상한
- 단위 시간당 요청 수 제한 (운영 서버 부하 방지)

### 재시도 정책
- 5xx 응답 시 즉시 재호출 금지

### 실행 시점
- 운영 트래픽 피크 시간대 외 실행 권장

---

## ⚠️ 주의사항

- `.env` 파일은 절대 GitLab에 올리지 마세요
- Production 환경에 부하 테스트 직접 실행 금지
- 테스트 중 500 에러 발생 시 즉시 중단
