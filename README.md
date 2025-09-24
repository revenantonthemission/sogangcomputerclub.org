# Memo App - Cloud Native Architecture

FastAPI + SvelteKit 기반 메모 애플리케이션을 Docker, Kubernetes, Redis, Kafka를 활용한 클라우드 네이티브 아키텍처로 마이그레이션한 프로젝트입니다.

## 🏗️ 아키텍처 개요

### 기존 아키텍처
- **Backend**: FastAPI + Gunicorn
- **Frontend**: SvelteKit
- **Database**: MariaDB
- **Web Server**: Nginx
- **Deployment**: 단일 서버

### 새로운 클라우드 네이티브 아키텍처
- **Container Platform**: Docker
- **Orchestration**: Kubernetes
- **Cache Layer**: Redis
- **Message Queue**: Apache Kafka
- **Database**: MariaDB (StatefulSet)
- **API Gateway**: Kubernetes Ingress
- **Service Mesh**: 마이크로서비스 패턴

## 🚀 기능

### Core Features
- **메모 CRUD**: 생성, 조회, 수정, 삭제
- **검색 기능**: 제목 및 내용 기반 검색
- **태그 시스템**: 메모 분류 및 관리
- **우선순위**: 4단계 우선순위 설정

### Cloud Native Features
- **Redis 캐싱**: 메모 조회 성능 최적화 (5분 TTL)
- **Kafka 이벤트**: 메모 생성/삭제 이벤트 스트리밍
- **Health Check**: 모든 서비스 상태 모니터링
- **High Availability**: Pod 복제를 통한 고가용성
- **Auto Scaling**: Kubernetes HPA 지원

## 📦 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| FastAPI | 8000 | 메인 API 서버 |
| MariaDB | 3306 | 메인 데이터베이스 |
| Redis | 6379 | 캐시 레이어 |
| Kafka | 9092 | 메시지 브로커 |
| Zookeeper | 2181 | Kafka 코디네이터 |

## 🔧 배포 방법

### 1. Docker Compose (개발환경)
```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 2. Kubernetes (운영환경)
```bash
# 이미지 빌드
docker build -t sgcc-fastapi:latest .

# Kubernetes 배포
cd k8s
chmod +x deploy.sh
./deploy.sh

# 상태 확인
kubectl get pods -n sgcc-memo
kubectl get svc -n sgcc-memo
kubectl get ingress -n sgcc-memo
```

### 3. 애플리케이션 접속
- **개발환경**: http://localhost:8000
- **운영환경**: http://sogangcomputerclub.org

## 🔍 모니터링 및 헬스 체크

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

### Response Example
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "kafka": "healthy"
  }
}
```

## 📊 Redis 캐싱 전략

- **키 패턴**: `memo:{memo_id}`
- **TTL**: 300초 (5분)
- **무효화**: 메모 수정/삭제 시 자동 삭제

## 📨 Kafka 이벤트 스트림

### Topic: `memo_events`

#### 메모 생성 이벤트
```json
{
  "event_type": "memo_created",
  "memo_id": 123,
  "title": "새 메모",
  "author": "사용자",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

#### 메모 삭제 이벤트
```json
{
  "event_type": "memo_deleted",
  "memo_id": 123,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 🔒 보안 설정

### Environment Variables
```bash
DATABASE_URL=mysql+aiomysql://user:password@db:3306/memo_app
REDIS_URL=redis://redis:6379
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### Kubernetes Secrets (권장)
```bash
kubectl create secret generic app-secrets \
  --from-literal=db-password=secure-password \
  --from-literal=db-user=memo_user \
  -n memo-app
```

## 🛠️ 개발 가이드

### 로컬 개발 환경 설정
```bash
# Python 가상환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 코드 구조
```
production/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 애플리케이션
│   └── services.py      # Redis/Kafka 서비스 (참고용)
├── k8s/
│   ├── namespace.yaml   # 네임스페이스
│   ├── configmap.yaml   # 설정
│   ├── mariadb.yaml     # 데이터베이스
│   ├── redis.yaml       # 캐시
│   ├── kafka.yaml       # 메시지 큐
│   ├── fastapi.yaml     # API 서버
│   ├── ingress.yaml     # 외부 접근
│   └── deploy.sh        # 배포 스크립트
├── Dockerfile           # 컨테이너 이미지
├── docker-compose.yml   # 개발 환경
├── nginx.conf           # 웹 서버 설정
├── requirements.txt     # Python 의존성
└── README.md           # 문서
```

## 📈 성능 최적화

### 1. 캐싱 전략
- Redis를 통한 자주 조회되는 메모 캐싱
- 캐시 히트율 모니터링
- TTL 기반 자동 만료

### 2. 데이터베이스 최적화
- Connection Pool 설정 (10-20 connections)
- 인덱스 활용 (id, title, created_at)
- 비동기 쿼리 처리

### 3. Kubernetes 리소스
- CPU: 100m-500m
- Memory: 256Mi-1Gi
- HPA: CPU 70% 기준 자동 스케일링

## 🚨 트러블슈팅

### 일반적인 문제들

1. **Kafka 연결 실패**
   ```bash
   kubectl logs -f deployment/kafka -n sgcc-memo
   ```

2. **Redis 연결 실패**
   ```bash
   kubectl exec -it deployment/redis -n sgcc-memo -- redis-cli ping
   ```

3. **데이터베이스 연결 실패**
   ```bash
   kubectl exec -it statefulset/mariadb -n sgcc-memo -- mysql -u root -p
   ```

### 로그 확인
```bash
# 전체 서비스 로그
kubectl logs -f deployment/fastapi -n sgcc-memo

# 특정 Pod 로그
kubectl logs -f <pod-name> -n sgcc-memo
```

## 🎯 향후 개선사항

- [ ] Prometheus + Grafana 모니터링 대시보드
- [ ] Elasticsearch + Kibana 로그 분석
- [ ] Istio 서비스 메시 도입
- [ ] ArgoCD GitOps 파이프라인
- [ ] JWT 인증/인가 시스템
- [ ] Rate Limiting
- [ ] API 버전 관리