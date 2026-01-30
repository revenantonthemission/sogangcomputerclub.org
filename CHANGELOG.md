# 변경 로그 (Changelog)

이 프로젝트의 모든 주요 변경 사항을 이 파일에 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 기반으로 하며,
이 프로젝트는 [시맨틱 버저닝](https://semver.org/lang/ko/)을 따릅니다.

## [0.2.0]

### Added
- CHANGELOG.md 파일 추가

### Changed
- Rate Limiter 메모리 누수 수정 (빈 키 삭제 로직 추가)
- 검색 API에 페이지네이션 지원 추가
- MEMO_COUNT 메트릭 초기화 타이밍 수정
- Kafka 메시지 발행 로직에 일관된 try-except 추가
- GitHub Actions 리팩토링 (공통 액션 추출)
- Frontend MVC 패턴 구현
- Docker Compose 설정 리팩토링 (base.yml 분리)
- Nginx 설정 중복 제거

### Removed
- 백업 스크립트에서 하드코딩된 기본 비밀번호 제거
- 미사용 EventService 코드 제거

### Security
- CORS 설정 제한 강화
- LIKE 쿼리 패턴 이스케이프 (SQL 와일드카드 인젝션 방지)
- 페이지네이션 limit 최대값 제한 (100개)
- Prometheus 레이블 카디널리티 최적화 (경로 파라미터 정규화)

---

## [0.1.0] - 2025-12-10

### Added
- **Backend**: FastAPI + SQLAlchemy 기반 메모 CRUD API
  - 메모 생성, 조회, 수정, 삭제
  - 키워드 검색 기능
  - Pydantic 스키마 검증
- **Frontend**: SvelteKit + TypeScript 기반 웹 UI
  - 반응형 디자인
  - Tailwind CSS 스타일링
- **Infrastructure**
  - Docker Compose 기반 로컬/프로덕션 환경
  - PostgreSQL 데이터베이스
  - Redis 캐시
  - Apache Kafka 메시지 큐
  - Nginx 리버스 프록시 + SSL (Let's Encrypt)
- **Monitoring**
  - Prometheus 메트릭 수집
  - Grafana 대시보드
- **CI/CD**
  - GitHub Actions 워크플로우 (테스트, 빌드, 배포)
  - 자동 보안 스캔 (Trivy, CodeQL, TruffleHog)
  - PR 자동 레이블링 및 검증
- **Documentation**
  - README.md (아키텍처, 빠른 시작, Docker 명령어)
  - CONTRIBUTING.md (GitHub Flow 워크플로우)
  - CODE_OF_CONDUCT.md (Contributor Covenant)
  - SECURITY.md (취약점 신고 절차)

---

## 버전 관리 가이드

### 버전 형식
`MAJOR.MINOR.PATCH` (예: `1.2.3`)

- **MAJOR**: 하위 호환되지 않는 API 변경
- **MINOR**: 하위 호환되는 기능 추가
- **PATCH**: 하위 호환되는 버그 수정

### 릴리스 프로세스
1. `CHANGELOG.md`의 `[Unreleased]` 섹션을 새 버전으로 이동
2. 버전 태그 생성: `git tag -a v1.0.0 -m "Release v1.0.0"`
3. 태그 푸시: `git push origin v1.0.0`
4. GitHub Actions `release.yml`이 자동으로 릴리스 생성

---

[Unreleased]: https://github.com/Sogang-Computer-Club/sogangcomputerclub.org/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Sogang-Computer-Club/sogangcomputerclub.org/releases/tag/v0.1.0
