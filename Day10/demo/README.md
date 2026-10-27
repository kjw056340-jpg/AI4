# note-demo

회원 기능과 제목·내용 중심의 간단한 게시판 목업입니다.

**문서 확인일: 2026-10-27 (Asia/Seoul).** 공식 Node.js·GitHub 문서를 확인해 실행 기준과 배포 절차를 갱신했습니다. 현재 구현은 브라우저 저장소 기반이며 DB 연결은 향후 단계입니다.

## 1. 구현 범위

| 기능 | 구현 내용 |
| --- | --- |
| 회원가입 | 이메일, 닉네임, 비밀번호 입력 및 중복 이메일 검사 |
| 로그인·로그아웃 | 브라우저에 저장된 목업 계정으로 로그인·로그아웃 |
| 비밀번호 찾기 | 이메일 입력 후 목업 안내. 실제 메일 전송·비밀번호 변경 없음 |
| 게시판 | 제목 검색, 10개씩 페이징, 상세 조회, 글 등록 |
| 수정·삭제 | 작성자 본인만 가능. 글 삭제 시 연결된 댓글도 삭제 |
| 댓글 | 로그인한 회원이 상세 화면에서 작성 |
| 마스킹 | 제목·본문·댓글·닉네임의 금칙어를 별표로 표시 |
| 관리자 | 키워드 추가·삭제, 마스킹 미리보기, 참고 자료 확인 |

화면은 **목록 / 상세 / 글쓰기·수정 / 계정 팝업 / 금칙어 관리** 5종입니다. ‘내가 쓴 글’은 목록의 작성자 필터입니다.

## 2. 실행 환경

- 권장: **Node.js 24 LTS의 최신 패치**. 확인일 기준 공식 다운로드 표시는 **v24.22.1 LTS**입니다. [공식 다운로드](https://nodejs.org/en/download), [지원 상태](https://nodejs.org/en/about/previous-releases)
- 최신 Chrome, Edge, Firefox 또는 Safari.
- 외부 패키지 의존성이 없어 `npm install`과 빌드가 필요 없습니다. npm이 없어도 Node.js만으로 실행·테스트할 수 있습니다.

## 3. 로컬 실행

프로젝트 폴더에서 실행합니다. Windows PowerShell 예시:

```powershell
cd C:\Users\Playdata\dev\Day10\demo
node --version
node server.js
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 엽니다. 종료는 실행한 터미널에서 `Ctrl+C`를 누릅니다.

다른 포트로 실행하려면:

```powershell
$env:PORT = '3001'
node server.js
```

다음 실행에서 기본 포트로 돌아가려면 `Remove-Item Env:PORT -ErrorAction SilentlyContinue`를 실행합니다. macOS·Linux에서는 `PORT=3001 node server.js`로 실행할 수 있습니다.

npm이 설치된 환경에서는 `npm start`, `npm run dev`, `npm test`도 지원합니다. `public/index.html`을 직접 더블클릭하면 모듈 로딩이 제한되므로 HTTP 서버로 접속해야 합니다. 로컬 서버는 현재 컴퓨터의 `127.0.0.1`에만 바인딩됩니다.

### 데모 계정

로그인 팝업의 **일반 회원** 또는 **관리자** 버튼으로 바로 체험할 수 있습니다.

| 계정 | 이메일 | 비밀번호 |
| --- | --- | --- |
| 일반 회원 | demo@note.demo | demo1234 |
| 관리자 | admin@note.demo | admin1234 |

첫 실행 시 샘플 게시글 23개가 준비됩니다. 테스트용으로 새 회원을 가입해 사용할 수도 있습니다.

## 4. 테스트

```powershell
node --test
```

JavaScript 문법 검사:

```powershell
node --check server.js
node --check public/app.js
node --check public/model.js
```

**2026-10-27 실제 실행 결과: 자동 테스트 11개 통과, 실패 0개. 위 문법 검사 3개 통과.** 로컬 검증 환경은 Windows / Node.js v24.19.0입니다. 권장 최신 패치 버전에서의 로컬 재검증은 수행하지 않았습니다.

| 테스트 파일 | 검증 내용 |
| --- | --- |
| `tests/model.test.js` | 페이징·마지막 페이지, 금칙어와 변형 표현, 사전 변경의 소급 적용, 가입 검증, 작성자 권한 (5개) |
| `tests/server.test.js` | 실제 서버의 HTML·CSS·JS 응답, 문자 인코딩, 자산 경로, 프로젝트 파일 접근 차단, 경로 이탈 차단, 잘못된 URL 처리 (6개) |

HTTP 테스트는 비어 있는 임시 포트에서 서버를 실행하고 종료합니다. 하위 경로 검증은 자산 URL 계산을 검사하며, 실제 GitHub Pages에 배포한 브라우저 검증을 대신하지 않습니다. SQL 실행·실제 이메일·SNS 인증 테스트는 현재 구현 범위에 포함되지 않습니다.

### 수동 확인 순서

1. 비회원으로 목록의 1·2·3페이지를 열어 10·10·3개씩 표시되는지 확인합니다.
2. 회원가입 후 로그인·로그아웃하고 제목 검색을 확인합니다.
3. 일반 회원으로 글을 작성·수정하고 댓글을 작성합니다. 새로고침 후에도 유지되는지 확인합니다.
4. 다른 회원의 상세 화면에는 수정·삭제 버튼이 없는지 확인합니다.
5. 직접 작성한 테스트 글을 삭제하고 목록에서 사라지는지 확인합니다.
6. 관리자로 로그인해 테스트 키워드를 추가한 뒤 미리보기와 기존 글에서 마스킹을 확인합니다. 해당 테스트 키워드를 삭제하면 다시 원문이 표시되는지 확인합니다.
7. 비밀번호 찾기에서 실제 메일이 전송되지 않았다는 목업 안내를 확인합니다.

위 순서는 재현용 확인 목록입니다. 이번 갱신에서 모든 수동 시나리오를 재수행한 것은 아닙니다.

## 5. GitHub Pages 배포

현재 앱은 `public/`의 정적 파일만으로 동작하므로 GitHub Pages에 게시할 수 있습니다. **이번 작업에서는 배포 설정 파일을 생성했으며 실제 외부 배포는 수행하지 않았습니다.**

### 준비

1. GitHub 저장소를 준비하고 이 프로젝트 전체를 기본 브랜치 `main`에 업로드합니다. `.github/workflows/deploy-pages.yml`도 포함합니다.
2. 저장소 **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
3. **Actions** 탭에서 워크플로 사용이 허용되어 있는지 확인합니다.

GitHub Free에서는 공개 저장소를 사용합니다. 비공개 저장소의 Pages 지원은 계정 요금제에 따라 다르며, 저장소 공개 여부와 사이트 접근 범위는 별도로 확인해야 합니다. [공식 Pages 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

### 배포 실행

1. 설정 완료 후 `main`에 변경을 푸시하거나 **Actions → Test and deploy note-demo → Run workflow**에서 `main`을 선택합니다.
2. `test` 작업이 성공한 뒤 `deploy` 작업이 실행됩니다. 테스트가 실패하면 배포되지 않습니다.
3. 완료된 작업의 `github-pages` 환경 또는 **Settings → Pages**에서 실제 배포 주소를 확인합니다.
4. 사이트에서 CSS·JS 로딩, 로그인 팝업, 페이징·댓글·관리자 기능을 확인합니다.

일반적인 프로젝트 사이트 주소 형식은 `https://<계정명>.github.io/<저장소명>/`입니다. 실제 주소는 배포 결과에 표시된 값을 사용합니다. 사용자·조직 대표 저장소 또는 사용자 지정 도메인은 주소 형태가 다릅니다.

### 배포 설정의 동작

- `main` 푸시·수동 실행: 테스트 성공 후 배포.
- `main` 대상 Pull Request: 테스트만 실행.
- 업로드 대상: **`public/`만**. README·SQL·테스트·로컬 서버 코드는 게시하지 않습니다.
- 파일 설치·번들 빌드 없음. `.js`·`.css`는 상대 경로를 사용해 저장소 하위 URL을 지원합니다.
- 테스트 작업은 `contents: read`, 배포 작업은 추가로 `pages: write`·`id-token: write`를 사용합니다.
- 기본 브랜치가 `main`이 아니면 워크플로의 `branches` 두 곳과 `refs/heads/main` 조건을 실제 브랜치로 변경합니다.

공식 자료에서 확인한 액션 버전은 `checkout@v7`, `setup-node@v7`, `configure-pages@v5`, `upload-pages-artifact@v4`, `deploy-pages@v4`입니다. 외부 GitHub Actions 실행은 아직 확인하지 않았습니다. [checkout](https://github.com/actions/checkout), [setup-node](https://github.com/actions/setup-node), [Pages 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

### 갱신·되돌리기

변경 내용을 `main`에 푸시하면 재검증 후 새 버전이 배포됩니다. 잘못된 변경은 해당 커밋을 되돌려 `main`에 반영한 뒤 다시 배포합니다. 코드 배포는 사용자 브라우저의 저장 데이터를 이전 상태로 복구하지 않습니다.

다른 정적 호스팅을 사용할 때도 게시 디렉터리는 `public/`, 별도 빌드 명령은 없습니다. HTTPS를 지원하는 호스팅을 사용합니다. 이 프로젝트의 Node 서버는 로컬 확인용입니다.

## 6. 저장 방식 및 현재 한계

- 회원·비밀번호·세션·게시글·댓글·키워드는 브라우저 `localStorage`의 `note-demo-v1`에 저장됩니다.
- **비밀번호는 평문 목업**입니다. 실제 사용하는 비밀번호나 개인정보를 입력하지 마세요.
- 계정·권한 검사는 화면 체험용입니다. 실제 서비스의 서버 인증·관리자 접근 통제를 제공하지 않습니다.
- 접속자·브라우저별 데이터가 분리되므로, 배포해도 여러 사용자가 같은 게시판이나 금칙어 사전을 공유하지 않습니다.
- `localhost`와 배포 사이트, 다른 포트·브라우저는 저장소가 다릅니다. 배포 주소로 옮기면 새로운 초기 데이터가 나타나는 것이 정상입니다.
- 초기화하려면 해당 사이트의 개발자 도구 **Application → Local Storage**에서 `note-demo-v1`만 삭제하고 새로고침합니다. 그 사이트의 목업 데이터는 사라집니다.
- 금칙어 목록은 공개 자료를 참고한 14개 데모 목록이며 자동 갱신되지 않습니다. 관리자가 추가·삭제할 수 있고, 문맥에 따른 오탐·누락이 있을 수 있습니다.
- Google Fonts 연결이 없어도 기본 글꼴로 표시됩니다.

실제 공동 게시판으로 전환할 때는 서버 API·DB 연결, 비밀번호 해시, 서버 세션과 권한 검증, 비밀번호 재설정 메일 및 SNS 인증을 구현해야 합니다.

## 7. 파일 및 설계 문서

```text
public/                      화면·브라우저 로직·스타일 (배포 대상)
server.js                    로컬 정적 서버
tests/                       모델·HTTP 자동 테스트
.github/workflows/           테스트 및 GitHub Pages 배포 설정
docs/implementation-plan.md   구현 및 검증 계획
docs/design.md               최소 화면 구성·ERD·테이블 명세
schema.sql                   향후 PostgreSQL 테이블 생성 SQL
```

- [구현 및 검증 계획](docs/implementation-plan.md)
- [최소 화면 구성·ERD·테이블 명세](docs/design.md)
- [PostgreSQL 테이블 생성 SQL](schema.sql)
- [배포 워크플로](.github/workflows/deploy-pages.yml)

SQL은 현재 앱에 자동 적용되지 않습니다. 현재 UUID·중첩 댓글·문자열 금칙어 배열은 DB 도입 시 설계 문서의 관계형 테이블로 매핑합니다. 초기 금칙어의 참고 자료·조사일은 설계 문서와 관리자 화면에 있습니다.

## 8. 문제 해결

| 증상 | 확인할 내용 |
| --- | --- |
| `node` 명령을 찾을 수 없음 | 공식 Node.js 24 LTS 설치 후 터미널을 다시 열고 `node --version` 확인 |
| `npm` 명령이 없음 | 필수 도구가 아님. `node server.js`, `node --test` 사용 |
| `EADDRINUSE` | 다른 포트를 지정하거나 기존 서버를 종료 |
| 빈 화면 | HTTP 주소로 열었는지, Console 오류 및 JS 요청 상태 확인 |
| Pages에서 CSS·JS 404 | `public/`이 업로드되었는지, 상대 경로를 유지했는지, 배포 작업이 성공했는지 확인 |
| Pages 배포 권한 오류 | Source가 GitHub Actions인지, 워크플로 권한·`github-pages` 환경의 브랜치 제한 확인 |
| 배포 작업 자체가 없음 | `main` 푸시 또는 `main`을 선택한 수동 실행인지 확인. PR에서는 테스트만 수행 |
| 새 브라우저에서 작성 글이 없음 | 현재 데이터는 각 브라우저 저장소에만 존재 |

## 9. 공식 참고 자료

아래 문서를 **2026-10-27**에 확인했습니다. 이후 설치·배포 시 공식 페이지의 최신 상태를 다시 확인할 수 있습니다.

- [Node.js 다운로드](https://nodejs.org/en/download) — LTS 다운로드 기준.
- [Node.js 릴리스 및 지원 상태](https://nodejs.org/en/about/previous-releases) — 지원 버전 확인.
- [GitHub Pages 게시 원본 설정](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — Source 설정 절차.
- [GitHub Pages 사용자 지정 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) — 업로드·배포·권한·환경 구성.
- [actions/checkout](https://github.com/actions/checkout) 및 [actions/setup-node](https://github.com/actions/setup-node) — 현재 액션 사용법.
