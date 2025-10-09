# sogangcomputerclub.org

서강대학교 중앙컴퓨터동아리 SGCC의 공식 웹사이트가 담긴 레포지토리입니다.

홈페이지는 FastAPI + SvelteKit 기반으로 설계되었으며, SGCC의 공식 서버에서는 홈페이지를 서비스하기 위해 Docker, Kubernetes, Redis, Kafka를 비롯한 클라우드 네이티브 아키텍처를 채택하고 있습니다.

## 🏗️ 아키텍처

```text
                    ┌──────────┐
                    │ Certbot  │
                    │ (SSL)    │
                    └────┬─────┘
                         │
          ┌──────────────▼──────────────┐
          │   Nginx (Reverse Proxy)     │
          │    sogangcomputerclub.org   │
          └──────────┬──────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
     ┌────▼─────┐          ┌────▼─────┐
     │ Frontend │          │ Backend  │
     │SvelteKit │          │ FastAPI  │
     │  :3000   │          │  :8000   │
     └──────────┘          └────┬─────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
          ┌────▼─────┐     ┌────▼────┐      ┌────▼─────┐
          │ MariaDB  │     │  Redis  │      │  Kafka   │
          │  :3306   │     │  :6380  │      │  :9092   │
          └──────────┘     └─────────┘      └────┬─────┘
                                                 │
                                            ┌────▼─────┐
                                            │Zookeeper │
                                            │  :2181   │
                                            └──────────┘
```

### 기술 스택

#### Backend

- FastAPI
- Uvicorn ASGI 서버
- MariaDB 데이터베이스
- SQLAlchemy ORM

#### Frontend

- SvelteKit + TypeScript
- Tailwind CSS
- Vite 빌드 도구

#### Infrastructure

- Docker & Docker Compose
- Nginx 리버스 프록시
- Redis (캐시)
- Apache Kafka + Zookeeper (메시지 큐)
- Certbot (SSL/TLS 인증서)
- Kubernetes (선택적 배포)

## 🚀 빠른 시작

### 필수 요구사항

- Docker & Docker Compose
- Git

### 1. 프로젝트 클론

```bash
git clone https://github.com/your-org/sogangcomputerclub.org.git
cd sogangcomputerclub.org
```

### 2. 서비스 실행

```bash
docker-compose up -d
```

### 3. 접속

- **프론트엔드**: http://localhost:3000 (직접 접속)
- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Redis**: localhost:6380
- **MariaDB**: localhost:3306
- **Kafka**: localhost:9092

## 📁 프로젝트 구조

```text
sogangcomputerclub.org/
├── app/                        # Backend (FastAPI)
│   ├── __init__.py
│   ├── main.py                 # 메인 API 애플리케이션
│   └── services.py             # Redis/Kafka 서비스 로직
├── tests/                      # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py             # pytest 설정 및 fixture
│   ├── test_health.py          # Health check 테스트
│   ├── test_memos.py           # 메모 API 단위 테스트
│   ├── integration/            # 통합 테스트
│   │   ├── __init__.py
│   │   ├── test_docker_services.py  # Docker 서비스 상태 테스트
│   │   ├── test_database.py         # MariaDB 연결 테스트
│   │   ├── test_redis.py            # Redis 연결 테스트
│   │   ├── test_kafka.py            # Kafka 연결 테스트
│   │   └── test_api_e2e.py          # E2E API 테스트
│   └── load/                   # 부하 테스트
│       ├── locustfile.py       # Locust 트래픽 테스트
│       └── performance_test.py # 성능 측정 스크립트
├── scripts/                    # 유틸리티 스크립트
│   └── init_test_db.py         # CI용 데이터베이스 스키마 초기화
├── frontend/                   # Frontend (SvelteKit)
│   ├── src/                    # 소스 코드
│   │   ├── routes/             # SvelteKit 라우트
│   │   ├── lib/                # 공유 컴포넌트/유틸
│   │   │   ├── components/     # Svelte 컴포넌트
│   │   │   └── utils/          # 유틸리티 함수
│   │   ├── __tests__/          # 테스트 파일
│   │   │   └── routes/         # 페이지 테스트
│   │   ├── vitest-env.d.ts     # Vitest 타입 선언
│   │   └── app.html            # HTML 템플릿
│   ├── static/                 # 정적 파일
│   ├── Dockerfile              # Frontend 컨테이너 이미지
│   ├── package.json            # Node.js 의존성
│   ├── vitest.config.ts        # Vitest 설정
│   ├── vitest-setup.ts         # 테스트 환경 설정
│   ├── tsconfig.json           # TypeScript 설정
│   └── svelte.config.js        # Svelte 설정
├── k8s/                        # Kubernetes 매니페스트
│   ├── namespace.yaml
│   ├── mariadb.yaml
│   ├── redis.yaml
│   ├── kafka.yaml
│   ├── fastapi.yaml
│   ├── frontend.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── kind-config.yaml
│   └── deploy.sh
├── backups/                    # 데이터베이스 백업
│   └── README.md               # 백업/복구 가이드
├── .github/                    # GitHub 설정
│   ├── workflows/              # GitHub Actions CI/CD
│   │   ├── backend-ci.yml      # Backend 테스트 자동화
│   │   ├── frontend-ci.yml     # Frontend 테스트 자동화
│   │   ├── docker-build.yml    # Docker 이미지 빌드/푸시
│   │   └── integration-tests.yml # 통합 테스트 자동화
│   └── ISSUE_TEMPLATE/         # 이슈 템플릿
├── docker-compose.yml          # Docker Compose 설정
├── Dockerfile                  # Backend 컨테이너 이미지
├── pyproject.toml              # Python 프로젝트 설정 및 의존성
├── uv.lock                     # uv 의존성 잠금 파일
├── nginx.conf                  # Nginx 메인 설정
├── nginx-sogangcomputerclub.conf  # 사이트별 Nginx 설정
├── nginx.sh                    # Nginx 시작 스크립트
├── certbot.sh                  # SSL 인증서 관리 스크립트
├── backup-database.sh          # DB 백업 스크립트
├── restore-database.sh         # DB 복구 스크립트
├── LICENSE                     # MIT 라이선스
├── CODE_OF_CONDUCT.md          # 행동 강령
└── SECURITY.md                 # 보안 정책
```

## 🛠️ 개발 환경 설정

### Backend 로컬 개발

```bash
# uv 설치 (설치되지 않은 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치 및 가상환경 자동 생성
uv sync

# 개발 서버 실행
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 로컬 개발

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build
```

## 🗄️ 데이터베이스

### 백업 생성

```bash
./backup-database.sh
```

백업 파일은 `backups/` 디렉토리에 타임스탬프와 함께 저장됩니다.
최근 30개의 백업만 자동으로 유지됩니다.

### 복구

```bash
./restore-database.sh backups/memo_app_backup_20251006_025125.sql.gz
```

자세한 내용은 [backups/README.md](backups/README.md)를 참조하세요.

### 자동 백업 설정

- 백업 주기: 매일 새벽 3시
- 백업 스크립트: /home/rvnnt/sogangcomputerclub.org/backup-database.sh
- 로그 파일: /home/rvnnt/sogangcomputerclub.org/backups/backup.log
- Cron 서비스: 실행 중 및 부팅 시 자동 시작 활성화

#### 백업 설정 확인

##### crontab 확인

```bash
crontab -l
```

##### 수동 백업 테스트

```bash
/home/rvnnt/sogangcomputerclub.org/backup-database.sh
```

##### 백업 로그 확인

```bash
tail -f /home/rvnnt/sogangcomputerclub.org/backups/backup.log
```

## 🐳 Docker 명령어

### 서비스 관리

```bash
# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f fastapi
docker-compose logs -f frontend
docker-compose logs -f nginx

# 서비스 재시작
docker-compose restart

# 개별 서비스 재시작
docker-compose restart fastapi

# 서비스 중지
docker-compose down

# 볼륨까지 완전 삭제
docker-compose down -v
```

### 컨테이너 접속

```bash
# Backend 컨테이너 접속
docker-compose exec fastapi /bin/bash

# MariaDB 접속
docker-compose exec mariadb mysql -umemo_user -pphoenix memo_app

# Redis CLI 접속
docker-compose exec redis redis-cli

# Nginx 설정 테스트
docker-compose exec nginx nginx -t

# Nginx 리로드
docker-compose exec nginx nginx -s reload
```

## ☸️ Kubernetes 배포

### 클러스터 배포

```bash
cd k8s

# 모든 리소스 배포
./deploy.sh

# 개별 배포
kubectl apply -f namespace.yaml
kubectl apply -f mariadb.yaml
kubectl apply -f fastapi.yaml
kubectl apply -f frontend.yaml
kubectl apply -f ingress.yaml
```

### 상태 확인

```bash
# Pod 상태
kubectl get pods -n sgcc

# 서비스 상태
kubectl get svc -n sgcc

# Ingress 상태
kubectl get ingress -n sgcc

# 로그 확인
kubectl logs -f deployment/fastapi -n sgcc
```

## 🔧 환경 설정

### Backend 환경 변수

`docker-compose.yml`에서 설정:

```yaml
environment:
  - DATABASE_URL=mysql+aiomysql://memo_user:phoenix@mariadb:3306/memo_app
  - REDIS_URL=redis://redis:6379
  - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### Frontend 환경 변수

`frontend/.env`:

```text
VITE_API_URL=http://localhost:8000
NODE_ENV=production
HOST=0.0.0.0
PORT=3000
```

### MariaDB 환경 변수

```yaml
environment:
  - MYSQL_ROOT_PASSWORD=rootpassword
  - MYSQL_DATABASE=memo_app
  - MYSQL_USER=memo_user
  - MYSQL_PASSWORD=phoenix
```

> ⚠️ **보안 주의**: 프로덕션 환경에서는 반드시 강력한 비밀번호로 변경하세요!

## 🧪 테스트

### Unit Tests (Backend)

#### 백엔드 API 엔드포인트에 대한 단위 테스트

```bash
# 모든 단위 테스트 실행
uv run pytest tests/ -v

# 특정 테스트 파일만 실행
uv run pytest tests/test_memos.py -v

# 커버리지와 함께 실행
uv run pytest tests/ --cov=app --cov-report=html
```

#### 테스트 항목

- Health check 엔드포인트
- 메모 CRUD 작업 (생성, 조회, 수정, 삭제)
- 메모 검색 기능
- 유효성 검증 및 에러 처리
- 페이지네이션

### Integration Tests (서버)

#### 실제 Docker 컨테이너와 연동하는 통합 테스트

```bash
# 먼저 Docker 서비스 시작
docker-compose up -d

# 서비스가 완전히 시작될 때까지 대기 (약 30초)
sleep 30

# 통합 테스트 실행
uv run pytest tests/integration/ -v

# 특정 통합 테스트만 실행
uv run pytest tests/integration/test_docker_services.py -v  # Docker 서비스 상태
uv run pytest tests/integration/test_database.py -v         # MariaDB 연결
uv run pytest tests/integration/test_redis.py -v            # Redis 연결
uv run pytest tests/integration/test_kafka.py -v            # Kafka 연결
uv run pytest tests/integration/test_api_e2e.py -v          # E2E API 테스트
```

#### 통합 테스트 항목

- Docker Compose 서비스 상태 확인
- MariaDB 데이터베이스 연결 및 CRUD
- Redis 캐시 작업 (set, get, delete, expiration)
- Kafka 메시지 전송 및 수신
- 전체 API 라이프사이클 (E2E)
- 동시 요청 처리

### Frontend 테스트

#### 컴포넌트 및 유틸리티 단위 테스트

```bash
cd frontend

# 모든 테스트 실행
npm run test

# 타입 체크
npm run check

# 프로덕션 빌드
npm run build
```

#### 테스트 항목

- **컴포넌트 테스트 (27개)**
  - Header, Footer, NavigationBar, FeedCard 등
- **유틸리티 테스트 (9개)**
  - slugify 함수
- **페이지 테스트 (4개)**
  - 홈페이지, Welcome 페이지

#### 테스트 환경

- Vitest + jsdom
- @testing-library/svelte
- @testing-library/jest-dom

#### 개발 서버 실행

```bash
npm run dev
```

### Load Tests (부하 테스트)

#### Locust를 이용한 트래픽 테스트

```bash
# CLI 모드로 실행
uv run locust -f tests/load/locustfile.py --host=http://localhost:8000

# Web UI 모드로 실행 (http://localhost:8089 접속)
uv run locust -f tests/load/locustfile.py --host=http://localhost:8000 --web-host=0.0.0.0

# Headless 모드 (자동 실행)
uv run locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 1m --headless
```

##### 테스트 시나리오

- Health check (30%)
- 메모 목록 조회 (50%)
- 메모 생성 (10%)
- 단일 메모 조회 (10%)

#### 성능 테스트

```bash
# 간단한 성능 측정 스크립트 실행
uv run python tests/load/performance_test.py
```

##### 측정 항목

- 엔드포인트별 응답 시간 (평균, 중앙값, 최소, 최대, 표준편차)
- 동시 요청 처리 성능 (10명, 50명, 100명)
- 초당 처리 가능한 요청 수 (RPS)

### 수동 테스트

```bash
# Health check
curl http://localhost:8000/health

# API 문서 확인
open http://localhost:8000/docs

# Redis 연결 테스트
docker-compose exec redis redis-cli ping
# 응답: PONG

# Kafka 토픽 확인
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# 모든 서비스 상태 확인
docker-compose ps

# 네트워크 연결 확인
docker-compose exec fastapi ping mariadb
docker-compose exec fastapi ping redis
docker-compose exec fastapi ping kafka
```

## 🚀 CI/CD

### GitHub Actions 워크플로우

프로젝트는 GitHub Actions를 통해 자동화된 CI/CD 파이프라인을 제공합니다.

#### 1. Backend CI (`.github/workflows/backend-ci.yml`)

##### Trigger

- `main`, `master`, `develop`, `feature/backend-*` 브랜치에 push
- app/, tests/, pyproject.toml, uv.lock 파일 변경 시
- Pull Request 생성 시

##### Jobs

- Python 3.13 환경에서 단위 테스트 실행
- 코드 커버리지 측정 및 Codecov 업로드
- 코드 린팅 (Ruff)

#### 2. Frontend CI (`.github/workflows/frontend-ci.yml`)

##### Trigger

- `main`, `master`, `develop`, `feature/frontend-*` 브랜치에 push
- frontend/ 디렉토리 변경 시
- Pull Request 생성 시

##### Jobs

- Node.js 20.x 환경에서 테스트 실행
- TypeScript 타입 체크 (svelte-check)
- 컴포넌트 및 유틸리티 단위 테스트 (Vitest)
- 프로덕션 빌드 검증
- 빌드 아티팩트 업로드

#### 3. Docker Build (`.github/workflows/docker-build.yml`)

##### Trigger

- `main`, `master` 브랜치에 push
- 버전 태그 (`v*.*.*`) 생성 시

##### Jobs

- Backend 및 Frontend Docker 이미지 빌드
- GitHub Container Registry (ghcr.io)에 자동 푸시
- 이미지 태깅 전략:
  - 브랜치명 태그
  - 시맨틱 버전 태그 (`v1.0.0`, `v1.0`)
  - Git SHA 태그

#### Docker 이미지 사용

```bash
# Backend 이미지 pull
docker pull ghcr.io/your-org/sogangcomputerclub.org/backend:latest

# Frontend 이미지 pull
docker pull ghcr.io/your-org/sogangcomputerclub.org/frontend:latest
```

#### 4. Integration Tests (`.github/workflows/integration-tests.yml`)

##### Trigger

- `main`, `master`, `develop`, `feature/backend-*` 브랜치에 push
- Pull Request 생성 시
- 매일 새벽 2시 (UTC) 자동 실행

##### Jobs

- MariaDB, Redis 서비스 컨테이너 시작
- 데이터베이스 스키마 초기화 (scripts/init_test_db.py)
- 데이터베이스 연결 테스트
- Redis 캐시 작업 테스트
- 테스트 결과 아티팩트 업로드

### 로컬에서 Docker 이미지 빌드

```bash
# Backend 이미지
docker build -t sogangcomputerclub/backend:latest .

# Frontend 이미지
docker build -t sogangcomputerclub/frontend:latest ./frontend
```

### 수동 이미지 푸시 (레지스트리 사용시)

```bash
docker push sogangcomputerclub/backend:latest
docker push sogangcomputerclub/frontend:latest
```

### SSL 인증서 발급 (Let's Encrypt)

Certbot 서비스가 자동으로 SSL 인증서를 관리합니다:

```bash
# certbot.sh 스크립트가 자동으로 실행됨
# 수동 갱신이 필요한 경우:
docker-compose restart certbot

# 인증서 확인
docker-compose exec certbot certbot certificates
```

## 🔒 보안

- SSL/TLS 인증서는 Let's Encrypt 사용 권장
- 프로덕션 환경에서는 반드시 환경 변수로 민감 정보 관리
- 데이터베이스 비밀번호 변경 필수
- CORS 설정 확인

자세한 내용은 [SECURITY.md](SECURITY.md)를 참조하세요.

## 🤝 프로젝트에 기여하기

기여는 언제나 환영합니다!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

행동 강령은 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)를 참조하세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 개발팀

### Infra/Database

- 조준희 (19 중국문화학과)

### Backend

- 김대원 (23 경제학과)
- 조준희 (19 중국문화학과)

### Frontend

- 김대원 (23 경제학과)
- 김주희 (24 미디어 엔터테인먼트)
- 정주원 (24 물리학과)
- 조인영 (25 인문 기반 자율전공)
- 허완 (25 컴퓨터공학과)

---

> Made by SGCC
