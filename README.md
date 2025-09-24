# sogangcomputerclub.org

SGCC 공식 홈페이지의 깃허브 레포지토리입니다.

홈페이지는 FastAPI + SvelteKit 기반으로 설계되었으며, SGCC의 공식 서버에서는 홈페이지를 서비스하기 위해 Docker, Kubernetes, Redis, Kafka를 비롯한 클라우드 네이티브 아키텍처를 채택하고 있습니다.

## 🏗️ 아키텍처 개요

### 기존 아키텍처
- **Backend**: FastAPI + Gunicorn
- **Frontend**: SvelteKit
- **Database**: MariaDB
- **Web Server**: Nginx
- **Deployment**: 단일 서버

### 클라우드 네이티브 아키텍처
- **Container Platform**: Docker
- **Orchestration**: Kubernetes
- **Cache Layer**: Redis
- **Message Queue**: Apache Kafka
- **Database**: MariaDB (StatefulSet)
- **API Gateway**: Kubernetes Ingress
- **Service Mesh**: 마이크로서비스 패턴


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
