# 엘리스 LXP QA 프로젝트

엘리스 LXP 서비스의 학습자/교육자 관련 API 기능을 검증하는 QA 프로젝트입니다.

- Part 1: `pytest` 기반 API 기능 테스트 자동화
- Part 2: `JMeter` 기반 부하 테스트 및 결과 분석

## 프로젝트 구조

```text
api-performance-test/
├─ conftest.py
├─ pytest.ini
├─ requirements.txt
├─ README.md
├─ utils/
│  ├─ __init__.py
│  └─ api_client.py
├─ tests/
│  ├─ __init__.py
│  ├─ article/
│  ├─ classhome/
│  ├─ classroom_course/
│  ├─ classroom_course_educator/
│  ├─ schedule/
│  └─ student/
└─ load_test/
   ├─ processed/
   ├─ raw_data/
   └─ scripts/
```

## 실행 환경

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에 아래 값을 설정합니다.

```env
LEARNER_TOKEN=your_learner_token
EDUCATOR_TOKEN=your_educator_token
BASE_URL_CLASSROOM=your_classroom_base_url
BASE_URL_REST=your_rest_base_url
CLASSROOM_ID=your_classroom_id
ACCOUNT_ID=your_account_id
EDUCATOR_CLASSROOM_ID=your_educator_classroom_id
```

## 테스트 실행

### 전체 테스트 실행

```bash
pytest
```

### 특정 도메인 테스트 실행

```bash
pytest tests/article
pytest tests/schedule
```

### 여러 폴더 한 번에 실행

```bash
pytest tests/article tests/schedule
```

## 디렉터리 역할

- `tests/`: 기능 도메인별 API 테스트 코드
- `utils/api_client.py`: 공통 API 호출 래퍼
- `conftest.py`: 공통 fixture, 토큰/URL 설정, 테스트용 데이터 준비
- `load_test/scripts/`: 부하 테스트 결과 전처리 및 시각화 스크립트
- `load_test/raw_data/`: 원본 부하 테스트 결과
- `load_test/processed/`: 후처리된 CSV 및 그래프 결과물

## 주의 사항

- `.env` 파일과 실제 토큰 값은 저장소에 커밋하지 않습니다.
- 운영 환경에 직접 부하 테스트를 실행하지 않습니다.
- 테스트 데이터 생성/수정이 포함된 경우 실행 대상 환경을 반드시 확인합니다.
