# 동시성 마켓

쇼핑몰에서 여러 상품의 재고·배송 정보를 동시에 조회하는 상황을 재현하는 FastAPI 학습 앱입니다. 실제 외부 서비스 대신 일정한 대기 시간을 넣어 동기 호출, 비동기 I/O, 동기 함수를 스레드로 분리한 경우를 비교합니다. 상품과 재고는 예시 데이터이며 실제 주문 기능은 없습니다.

## 실행 방법 (Windows / PowerShell)

기존 Day7/main.py 서버와 별도로 **8001 포트**를 사용합니다. 서버와 화면이 함께 제공되므로 터미널 하나로 실행할 수 있습니다.

### 현재 작업 환경에서 바로 실행

이 앱 폴더에 전용 `.venv`를 생성하고 패키지 설치 및 자동 검증을 완료했습니다. 현재 컴퓨터에서는 다음 명령으로 바로 실행할 수 있습니다.

```powershell
cd C:\Users\Playdata\dev
.\Day7\shop_concurrency\.venv\Scripts\python.exe -m uvicorn app:app --app-dir Day7/shop_concurrency --host 127.0.0.1 --port 8001 --workers 1
```

브라우저에서 **http://127.0.0.1:8001** 을 여세요. `.venv`는 Git에서 제외됩니다. 다른 컴퓨터에서 받았다면 아래 설치 과정을 진행하세요.

### 1. 프로젝트 루트에서 패키지 설치

IDE에서 기존에 사용하던 Python 환경이 활성화되어 있다면:

```powershell
cd C:\Users\Playdata\dev
python -m pip install -r Day7/shop_concurrency/requirements.txt
```

별도 가상환경을 사용하려면 다음 명령을 실행합니다. `py`가 설치되어 있고 실행 가능한 경우의 예시입니다.

```powershell
cd C:\Users\Playdata\dev\Day7\shop_concurrency
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. 서버 실행

프로젝트 루트에서, 패키지를 설치한 Python으로 실행합니다.

```powershell
cd C:\Users\Playdata\dev
python -m uvicorn app:app --app-dir Day7/shop_concurrency --host 127.0.0.1 --port 8001 --workers 1
```

위에서 별도 가상환경을 만들었다면 앱 폴더에서 다음 명령을 대신 실행합니다.

```powershell
cd C:\Users\Playdata\dev\Day7\shop_concurrency
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8001 --workers 1
```

`Application startup complete`가 나타나면 브라우저에서 **http://127.0.0.1:8001** 에 접속하세요. API 문서는 **http://127.0.0.1:8001/docs** 입니다. 종료는 터미널에서 `Ctrl+C`입니다.

비교할 때는 반드시 **단일 워커**를 사용하세요. 여러 워커가 요청을 분산하면 이벤트 루프 하나가 막히는 현상이 덜 드러납니다. 코드 수정 후에는 서버를 재시작하세요. HTML 파일을 직접 열거나 `uvicorn probe:app`을 실행하는 방식은 사용하지 않습니다.

## 화면 사용 방법

1. 동시 조회할 상품 수와 상품당 대기 시간을 고릅니다.
2. **동기 호출**을 누르고 전체 완료 시간과 서버 상태 확인 지연을 확인합니다.
3. 같은 설정으로 **비동기 호출**, **동기 함수 개선**을 실행합니다.
4. 아래 실험 기록에서 같은 조건의 결과를 비교합니다. 기록은 현재 페이지 메모리에만 저장되어 새로고침하면 초기화됩니다.

기본값인 3개 상품 × 2초에서 예상되는 결과:

| 방식 | 핵심 코드 | 전체 완료 시간 | 다른 요청에 미치는 영향 |
| --- | --- | --- | --- |
| 동기 호출 | `legacy_lookup()` → `time.sleep(2)` | 약 6초 | 이벤트 루프가 막혀 상태 확인도 지연 |
| 비동기 호출 | `await asyncio.sleep(2)` | 약 2초 | 대기 중 상태 확인에 응답 |
| 동기 함수 개선 | `await asyncio.to_thread(legacy_lookup, ...)` | 약 2초 | 동기 I/O 대기를 스레드로 분리 |

실제 측정에는 연결·스케줄링 시간이 포함됩니다. 브라우저가 여러 응답을 한꺼번에 받는 경우 개별 상품의 수신 시간이 비슷하게 보일 수 있습니다. 전체 시간과 상태 확인 지연을 함께 관찰하세요.

## 코드와 측정의 의미

- `app.py`: `FastAPI`, `asyncio`, `time.sleep`, `time.perf_counter`, `asyncio.to_thread`를 사용하는 서버입니다. 기존 Day7 예제를 확장했습니다.
- `static/index.html`, `style.css`, `app.js`: 별도 빌드가 필요 없는 HTML/CSS/JavaScript 화면입니다. `Promise.all`로 실제 상품 API 요청을 동시에 전송합니다. 응답이 와야 상품 조회가 완료됩니다.
- `verify.py`: `httpx.AsyncClient`, `asyncio.gather`로 별도 단일 워커 서버를 띄워 페이지/API와 동시성 차이를 검증합니다. 검사 후 해당 서버를 종료합니다.
- `requirements.txt`: 실행 및 검증 패키지 목록입니다. Python 3.10 이상을 사용하세요.

상품 요청은 최대 4개이며, 상태 확인 요청은 시작 0.15초 후부터 이전 응답을 받은 뒤 0.4초 간격으로 하나씩 보냅니다. 화면에는 상태 확인 요청의 **최대 왕복 시간**을 표시합니다. 상품당 서버 처리 시간은 핸들러 진입 이후 시간이라 요청이 대기열에서 기다린 시간은 포함하지 않습니다. 상품별 수신 시간과 전체 시간은 브라우저 기준입니다.

`async def`를 선언한다고 내부의 동기 호출이 자동으로 비동기가 되지는 않습니다. 이 앱의 동기 호출 버튼은 이를 보여 주기 위해 의도적으로 이벤트 루프를 막습니다. 반면 FastAPI에서 일반 `def` 엔드포인트를 만들면 프레임워크가 스레드풀에서 실행하므로 이 예제와 동작이 다릅니다.

`asyncio.sleep`은 실제 재고 서버 응답을 기다리는 I/O의 모형입니다. 실제 서비스에서는 `httpx.AsyncClient`나 비동기 DB 클라이언트를 `await`합니다. `to_thread`는 기존 동기 I/O 라이브러리를 사용할 때 유용하며, CPU 계산 자체를 빠르게 만드는 기법은 아닙니다. 화면 타이머는 브라우저에서 실행되므로 서버가 막혀도 계속 움직입니다.

## 자동 검증

작성 환경에서 실제 로컬 서버 검증 결과: 3개 상품 × 0.5초 기준 동기 호출 1.51초, 비동기 호출 0.53초, 스레드 분리 0.53초였습니다. 동기 호출 중 상태 확인 지연은 1.36초였으며, 페이지/API 응답과 입력값 검증도 통과했습니다. JavaScript 문법 검사를 통과했으며, 연결된 브라우저 부재로 시각적 렌더링과 버튼 클릭 검증은 수행하지 못했습니다.

패키지를 설치한 Python으로 프로젝트 루트에서 실행합니다. 서버를 미리 켤 필요가 없으며 빈 포트를 자동 선택합니다.

```powershell
python Day7/shop_concurrency/verify.py
```

별도 가상환경을 사용했다면 앱 폴더에서:

```powershell
.\.venv\Scripts\python.exe verify.py
```

## 실행이 안 될 때

- **`python` 또는 `py`를 찾을 수 없음**: IDE의 Python 인터프리터를 확인하고 해당 실행 파일의 전체 경로로 실행하세요. 명령어에 공백이 있으면 PowerShell에서 `& "C:\경로\python.exe" -m uvicorn ...` 형식을 사용합니다.
- **`did not find executable at ...`**: 기존 가상환경이 가리키는 원본 Python이 없거나 접근되지 않는 상태입니다. 실행 가능한 Python을 선택한 후 앱 폴더에 새 가상환경을 만드세요. 기존 환경 삭제는 필요하지 않습니다.
- **`No module named fastapi/uvicorn/httpx`**: 서버 실행에 사용하는 동일한 Python으로 `-m pip install -r ...` 명령을 실행하세요.
- **`Attribute "app" not found`**: 위의 `app:app` 실행 명령을 사용하세요. `probe.py`는 서버 앱이 아닙니다.
- **8001 포트 사용 중**: `--port 8002`로 바꾸고 브라우저에서도 `http://127.0.0.1:8002`를 여세요.
- **조회 실패 또는 시간 초과**: 서버 터미널의 오류를 확인하세요. 비교 중 다른 탭이나 기존 `probe.py`에서 같은 서버에 부하를 주지 않도록 하세요.
