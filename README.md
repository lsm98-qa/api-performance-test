# 엘리스 LXP QA 자동화 프로젝트

엘리스 LXP 서비스의 학습자/교육자 관점 API를 검증하기 위한 QA 자동화 프로젝트입니다.  
`pytest` 기반 기능 테스트 자동화와 `JMeter` 부하 테스트 결과 분석을 함께 구성하여 기능 정확성과 성능 지표를 함께 확인할 수 있도록 했습니다.

## 프로젝트 목표

- 학습자/교육자 관점의 주요 API 기능 검증 자동화
- Positive / Negative / Boundary 테스트 시나리오 구성
- JMeter 기반 부하 테스트 결과 후처리 및 시각화
- GitHub Actions 기반 CI 파이프라인 구축

## 프로젝트 구성

### 1. API 기능 테스트 자동화

- `pytest` 기반 API 테스트 자동화
- 클래스 홈, 학습 과목, 일정, 게시판, 학습자/교육자 관련 API 검증
- 정상 응답, 예외 응답, 권한 경계, 파라미터 오류, 응답 코드 검증

### 2. 부하 테스트 로그 분석

- `JMeter` 실행 결과 데이터 전처리
- 평균/최대/최소 응답 시간, 에러율, 병목 구간 분석
- 성능 지표 시각화를 통한 부하 테스트 결과 확인

### 3. CI 파이프라인

- GitHub Actions 기반 테스트 자동화 파이프라인 구성
- Python 환경 설정, 문법 검증, pytest 실행, 리포트 업로드 자동화
- 테스트 실패 시에도 리포트 확인이 가능하도록 파이프라인 흐름 구성

## 프로젝트 구조

api-performance-test/
├── conftest.py
├── pytest.ini
├── requirements.txt
├── README.md
├── utils/
│   └── api_client.py
├── tests/
│   ├── article/
│   ├── classhome/
│   ├── classroom_course/
│   ├── classroom_course_educator/
│   ├── schedule/
│   └── student/
├── load_test/
│   ├── raw_data/
│   ├── processed/
│   └── scripts/
└── .github/
    └── workflows/
        └── ci.yml

## 환경 설정

pip install -r requirements.txt

테스트 실행을 위해 `.env` 파일에 필요한 토큰과 리소스 값을 설정합니다.

LEARNER_TOKEN=
EDUCATOR_TOKEN=
EXPIRED_TOKEN=
BASE_URL_CLASSROOM=
BASE_URL_REST=
CLASSROOM_ID=
CLASSROOM_ID_V2=
COURSE_ID=
COURSE_ID_V2=
ORIGINAL_COURSE_ID=
LECTURE_ID=
BOARD_ARTICLE_ID=
BOARD_ARTICLE_ID_NO_TOKEN=
BOARD_ARTICLE_ID_BOUNDARY=

## 테스트 실행

pytest
pytest -v
pytest tests/classhome -v
pytest tests/classroom_course -v
pytest tests/schedule -v

## 부하 테스트 리포트 생성

python load_test/scripts/day6_data_check.py
python load_test/scripts/preprocess_summary_csv.py
python load_test/scripts/day7_avg_latency_graph.py
python load_test/scripts/day7_max_min_graphs.py
python load_test/scripts/day7_extra_graphs.py
python load_test/scripts/day7_bottleneck_graphs.py
python load_test/scripts/tsp_error_rate.py

## 주요 포인트

- 도메인별 테스트 구조 분리
- 공통 API Client를 통한 요청 로직 재사용
- fixture 기반 테스트 데이터 및 클라이언트 관리
- 환경 변수 기반 실행 구조 구성
- GitHub Actions 기반 CI 자동화
- 기능 테스트와 성능 분석 흐름 분리

## 실행 관련 안내

본 프로젝트는 엘리스 LXP 서비스의 실제 API를 대상으로 작성되었습니다.  
따라서 테스트 실행에는 부트캠프 실습 환경에서 제공된 계정, 권한, 클래스 ID, 게시글 ID 등의 리소스가 필요합니다.

외부 사용자가 저장소를 clone하더라도 유효한 토큰과 테스트 리소스가 없으면 API 테스트를 직접 실행할 수 없습니다.  
본 저장소는 아래 내용을 중심으로 검토할 수 있도록 구성했습니다.

- pytest 기반 API 테스트 구조
- Positive / Negative / Boundary 테스트 설계
- 공통 API Client 및 fixture 구성
- GitHub Actions 기반 CI 파이프라인 구성
- JMeter 부하 테스트 결과 전처리 및 시각화 코드
- 성능 병목 분석 및 리포트 작성 흐름
