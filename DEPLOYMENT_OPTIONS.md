# 배포 옵션 가이드

## 🎯 현재 완성된 항목
✅ FastAPI 애플리케이션 (Redis, Kafka 통합)
✅ Docker 컨테이너 설정
✅ Kubernetes 매니페스트 전체 (namespace: sgcc-memo)
✅ 로컬 SQLite 환경에서 API 테스트 완료

## 🔧 배포 환경별 옵션

### 1. 로컬 개발 환경 (현재 작동 중)
```bash
# 가상환경 활성화
source venv/bin/activate

# SQLite로 간단 실행
DATABASE_URL="sqlite+aiosqlite:///./memo_app.db" \
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 접속: http://127.0.0.1:8000
# 헬스체크: curl http://127.0.0.1:8000/health
```

### 2. Docker 환경 (네트워크 이슈 해결 후)

#### Option A: Docker 권한 문제 해결
```bash
# Docker 그룹에 사용자 추가 (재로그인 필요)
sudo usermod -aG docker $USER

# 재로그인 후
docker build -t sgcc-fastapi:latest .
docker-compose up -d
```

#### Option B: 개별 컨테이너 실행
```bash
# MariaDB 개별 실행 (권한 해결 후)
sudo docker run -d --name mariadb \\
  -e MYSQL_ROOT_PASSWORD=rootpassword \\
  -e MYSQL_DATABASE=memo_app \\
  -e MYSQL_USER=memo_user \\
  -e MYSQL_PASSWORD=phoenix \\
  -p 3306:3306 mariadb:10.11

# FastAPI는 로컬에서 MariaDB 연결
DATABASE_URL="mysql+aiomysql://memo_user:phoenix@localhost:3306/memo_app" \\
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Kubernetes 환경

#### 로컬 Kubernetes 클러스터 설치 옵션:

##### A. Minikube (추천)
```bash
# Minikube 설치 (Ubuntu/Debian)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 클러스터 시작
minikube start

# 배포 실행
cd k8s && ./deploy.sh

# 서비스 접속
minikube service fastapi-service -n sgcc-memo
```

##### B. K3s (가벼운 Kubernetes)
```bash
# K3s 설치
curl -sfL https://get.k3s.io | sh -

# 권한 설정
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 배포 실행
cd k8s && ./deploy.sh
```

##### C. Docker Desktop Kubernetes
```bash
# Docker Desktop 설정에서 Kubernetes 활성화
# Settings > Kubernetes > Enable Kubernetes

# 배포 실행
cd k8s && ./deploy.sh
```

### 4. 클라우드 환경 (운영)

#### AWS EKS
```bash
# eksctl로 클러스터 생성
eksctl create cluster --name sgcc-memo-cluster --region us-west-2

# 이미지를 ECR에 푸시
aws ecr create-repository --repository-name sgcc-fastapi
docker tag sgcc-fastapi:latest <account>.dkr.ecr.us-west-2.amazonaws.com/sgcc-fastapi:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/sgcc-fastapi:latest

# 매니페스트에서 이미지 경로 수정 후 배포
cd k8s && ./deploy.sh
```

#### Google GKE
```bash
# 클러스터 생성
gcloud container clusters create sgcc-memo-cluster --num-nodes=3

# 이미지를 GCR에 푸시
docker tag sgcc-fastapi:latest gcr.io/PROJECT_ID/sgcc-fastapi:latest
docker push gcr.io/PROJECT_ID/sgcc-fastapi:latest

# 배포
cd k8s && ./deploy.sh
```

## 📊 각 옵션별 장단점

| 옵션 | 장점 | 단점 | 적합한 상황 |
|------|------|------|-------------|
| 로컬 Python | 빠른 개발/테스트 | 의존성 관리 복잡 | 개발 초기 단계 |
| Docker | 환경 일관성 | 네트워크 설정 복잡 | 로컬 통합 테스트 |
| Minikube | 실제 K8s 환경 | 리소스 사용량 높음 | K8s 학습/테스트 |
| 클라우드 K8s | 운영 환경 준비 | 비용, 복잡성 | 실제 서비스 배포 |

## 🎯 추천 순서

1. **현재 환경에서 계속 개발**: 로컬 Python + SQLite
2. **Docker 권한 해결**: Docker 그룹 추가 후 재로그인
3. **Minikube 설치**: 로컬 Kubernetes 테스트 환경
4. **클라우드 배포**: AWS EKS 또는 GKE로 운영 환경 구축

## 💡 즉시 가능한 다음 단계

```bash
# 1. 현재 작동하는 애플리케이션 확장 테스트
curl -X POST "http://127.0.0.1:8000/memos/" -H "Content-Type: application/json" \\
  -d '{"title":"Kubernetes 테스트","content":"K8s 배포 준비 완료","tags":["k8s","배포"]}'

# 2. API 문서 확인
curl http://127.0.0.1:8000/docs

# 3. 헬스 체크로 서비스 상태 모니터링
watch -n 5 "curl -s http://127.0.0.1:8000/health | jq ."
```