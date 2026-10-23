# 무료 배포 검토

공식 문서 확인일: 2026-10-23 (한국 시간).
현재 코드는 무료 소규모 실행을 염두에 두었지만, 특정 업체의 무료 사용량이나 영구 보존을 보장하지 않습니다.
실제 배포, 결제 수단 등록, 유료 리소스 생성은 수행하지 않았습니다.

## 코드에서 줄인 자원

| 항목 | 적용 내용 |
| --- | --- |
| DB | 내장 SQLite 파일 한 개, 테이블 하나, 외래키·관계 없음 |
| 글 | 최대 1,000개. 작성자 20자·내용 1,000자 |
| 조회 | 한 요청에 최대 20개, 최대 50페이지 |
| 폼 | 전송 본문 16,384바이트까지 검증 |
| 화면 | 로컬 HTML·CSS. JS 빌드·CDN·폰트 다운로드 없음 |
| 서버 | Uvicorn worker 1개 권장 |
| 외부 비용 | 외부 DB·유료 API·이미지 저장·메일·백그라운드 작업 없음 |
| 운영 설치 | pytest·httpx는 운영 requirements에서 제외 |

글 저장량 제한은 호스팅의 CPU·메모리·트래픽 쿼터를 대신하지 않습니다.
검증 환경에서 작성자 20자·내용 1,000자의 한글 글 1,000개를 넣은 DB 파일은
4,112,384바이트(약 3.92 MiB)였습니다. 런타임·패키지·로그·백업 용량은 별도입니다.
폼 크기는 프레임워크가 본문을 받은 뒤 검증하므로 네트워크 단계의 업로드 제한과 다릅니다.
공개 익명 작성 방식이라 반복 등록을 하면 저장량이 가득 찰 수 있습니다.
고급 차단·로그인·자동 정리 알고리즘을 임의로 추가하지 않았습니다.
이 범위를 넘어서는 운영 요구가 생기면 사용자와 먼저 협의해야 합니다.

## 서비스별 판단

### Render Free: 데이터가 사라져도 되는 시연용

무료 Web Service의 로컬 파일은 재배포·재시작·유휴 종료 시 사라집니다.
유휴 15분이면 서비스가 내려가며 무료 서비스에는 영구 디스크를 붙일 수 없습니다.
따라서 SQLite 기록을 보존하는 방명록 운영에는 맞지 않습니다.
근거: [Render 무료 플랜 공식 안내](https://render.com/docs/free).

저장 자료가 없어져도 되는 시연만 원할 때 사용할 설정은 다음과 같습니다.
정적 사이트가 아니라 Python Web Service로 구성합니다.

| 설정 | 값 |
| --- | --- |
| 저장소 Root Directory | 이 수업 저장소는 `Day1-Day8`, 방명록 파일만 올린 별도 저장소는 비워 둠 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Instance Type | Free |
| 디스크·외부 DB | 추가하지 않음 |

Python 버전은 방명록 폴더의 `.python-version` 파일에 `3.13`으로 지정했습니다.
방명록만 별도 저장소로 옮긴 경우 숨김 파일인 `.python-version`도 `requirements.txt` 옆에 올려야 합니다.
현재 `pydantic==2.11.5`가 사용하는 `pydantic-core==2.33.2`에는 Python 3.14용 wheel이 없어
Render 기본 Python 3.14에서 Rust 소스 빌드를 시도하다 실패할 수 있습니다.
근거: [pydantic-core 배포 파일](https://pypi.org/project/pydantic_core/2.33.2/#files).

이미 이 오류가 난 서비스는 Render의 Environment에서 `PYTHON_VERSION`을 `3.13.9`로 설정하고
저장한 뒤 다시 배포하면 됩니다. 환경 변수는 `.python-version`보다 우선하며 패치 버전까지 필요합니다.
재배포 로그에서 `Using Python version 3.13.9`를 확인하세요.
근거: [Render Python 버전 설정](https://render.com/docs/python-version).

이 명령은 Linux 배포 서버용입니다. 로컬 실행은 README의 명령을 사용합니다.
무료 서비스의 사용량 소진 동작과 계정의 과금 설정은 배포 직전에 다시 확인해야 합니다.
유료 디스크를 붙여 문제를 해결하는 방식은 무료 조건을 벗어나므로 채택하지 않았습니다.

### PythonAnywhere: 계정에서 ASGI 조건 확인이 필요한 후보

일반 무료 계정 공식 안내에는 디스크 512 MiB, 웹 앱 하나·worker 하나·1개월 만료가 명시되어 있습니다.
SQLite는 전체 계정에서 사용할 수 있습니다.
근거: [무료 계정 기능](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/),
[데이터베이스 지원](https://help.pythonanywhere.com/pages/KindsOfDatabases/).

다만 FastAPI가 필요한 ASGI 사이트는 실험 기능이며, 공식 안내는 장기 가격 정책을 확정하지 않았다고 설명합니다.
따라서 일반 무료 웹 앱의 조건을 ASGI에 그대로 적용하거나 장기 무료 운영을 약속할 수 없습니다.
근거: [ASGI 공식 안내의 제한 사항](https://help.pythonanywhere.com/pages/ASGIAPI/).

계정에서 ASGI 무료 제공 여부, 파일 유지 조건, 만료 갱신 방법을 확인한 뒤에만 운영 후보로 결정해야 합니다.
별도 배포 CLI·패키지를 설치하는 절차는 사용자 협의 없이 추가하지 않았습니다.

## 영구 저장이 가능한 배포처를 정했을 때

1. FastAPI/ASGI 실행과 Python 버전 지원을 확인합니다.
2. 무료 범위에 영구 쓰기 가능 디렉터리가 포함되는지 확인합니다.
3. `requirements.txt`만 설치하고 Uvicorn을 worker 1개로 실행합니다.
4. `GUESTBOOK_DB_PATH`를 영구 디렉터리의 파일 절대 경로로 지정합니다.
5. 글 하나를 등록한 후 서버 재시작·재배포를 각각 실행하여 보존 여부를 확인합니다.
6. 사용량·앱 만료·백업 정책을 확인합니다. 무료 조건을 벗어나는 추가 리소스는 만들지 않습니다.

**현재 남은 배포 결정은 무료 ASGI와 SQLite 영구 보존을 함께 제공하는 계정·환경 선택입니다.**
요구사항을 맞추기 위해 다른 DB나 프레임워크로 바꾸는 작업은 사용자 승인 없이 진행하지 않습니다.
