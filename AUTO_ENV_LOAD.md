# 자동 .env 파일 로드 설정

## 개요

Spring Boot가 자동으로 `.env` 파일을 읽도록 설정했습니다. 이제 스크립트에서 환경 변수를 수동으로 로드할 필요가 없습니다.

## 구현 방법

### 1. dotenv-java 라이브러리 추가

`service.kroaddy.site/auth-service/build.gradle`에 추가:

```gradle
implementation 'io.github.cdimascio:dotenv-java:3.0.0'
```

### 2. ApiApplication에서 자동 로드

`ApiApplication.java`에서 애플리케이션 시작 시 `.env` 파일을 자동으로 읽어 시스템 속성으로 설정합니다.

## 장점

1. **보안**: 스크립트에서 환경 변수를 출력하지 않음
2. **편의성**: 수동으로 환경 변수를 설정할 필요 없음
3. **자동화**: Spring Boot 시작 시 자동으로 `.env` 파일 로드

## 사용 방법

### 1. .env 파일 위치

`.env` 파일은 **프로젝트 루트 디렉토리**에 있어야 합니다:

```
kroaddy_project_dacon/
├── .env                    ← 여기에 위치
├── service.kroaddy.site/
│   └── auth-service/
│       └── src/
│           └── main/
│               └── java/
│                   └── ApiApplication.java
```

### 2. 서비스 실행

```powershell
# Windows
.\scripts\start-auth-service.ps1
```

```bash
# Linux/Mac
./scripts/start-auth-service.sh
```

스크립트는 이제 환경 변수를 출력하지 않고, Spring Boot가 자동으로 `.env` 파일을 읽습니다.

## 확인

서비스 시작 시 로그에서 다음을 확인할 수 있습니다:

- `.env` 파일이 없거나 로드 실패 시: "Note: .env file not found..."
- 정상적으로 로드되면: 별도 메시지 없이 정상 시작

## 문제 해결

### .env 파일을 찾을 수 없는 경우

`ApiApplication.java`의 `directory("../..")` 경로를 확인하세요. 프로젝트 구조에 따라 조정이 필요할 수 있습니다.

### 환경 변수가 로드되지 않는 경우

1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. `.env` 파일 형식이 올바른지 확인 (`KEY=VALUE`)
3. 서비스 재시작

## 참고

- dotenv-java는 프로젝트 루트에서 `.env` 파일을 찾습니다
- 환경 변수는 시스템 속성으로 설정되어 Spring Boot의 `${ENV_VAR}` 형식으로 사용 가능합니다
- 기존 환경 변수가 있으면 우선순위가 높습니다

---

**작성일**: 2025년 1월

