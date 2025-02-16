# FastAPI Board Service

게시판 기능을 제공하는 FastAPI 기반의 RESTful API 서비스입니다.

## 기능

- 사용자 인증 (회원가입/로그인/로그아웃)
- 게시판 관리 (생성/조회/수정/삭제)
- 게시글 관리 (작성/조회/수정/삭제)
- Redis 기반 세션 관리
- 커서 기반 페이지네이션
- PostgreSQL 데이터베이스

## 시작하기

### 사전 요구사항

- Python 3.10 이상
- Docker 및 Docker Compose
- PostgreSQL
- Redis

### 설치

1. 저장소 클론
```bash
git clone <repository-url>
cd <project-directory>
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경변수 설정
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 다음 내용을 추가:

```plaintext
# Database
POSTGRES_USER=developer
POSTGRES_PASSWORD=devpassword
POSTGRES_DB=developer
POSTGRES_HOST=localhost
POSTGRES_PORT=25000

# Redis
REDIS_HOST=localhost
REDIS_PORT=25100
REDIS_DB=0

# JWT
SECRET_KEY=your-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Session
SESSION_EXPIRE_MINUTES=60
```

### 실행

1. Docker 컨테이너 실행
```bash
docker-compose up -d
```

2. FastAPI 서버 실행
```bash
uvicorn main:app --reload
```

서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

## API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


## API 엔드포인트

### 인증
- POST `/auth/signup` - 회원가입
- POST `/auth/token` - 로그인
- POST `/auth/refresh` - 토큰 갱신
- POST `/auth/logout` - 로그아웃

### 게시판
- POST `/boards` - 게시판 생성
- GET `/boards` - 게시판 목록 조회
- GET `/boards/{board_id}` - 특정 게시판 조회
- PUT `/boards/{board_id}` - 게시판 수정
- DELETE `/boards/{board_id}` - 게시판 삭제

### 게시글
- POST `/posts` - 게시글 작성
- GET `/posts/board/{board_id}` - 게시판의 게시글 목록 조회
- GET `/posts/{post_id}` - 특정 게시글 조회
- PUT `/posts/{post_id}` - 게시글 수정
- DELETE `/posts/{post_id}` - 게시글 삭제

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.