# Git 초기 설정 및 코드 업로드 가이드

로컬 PC의 작업 폴더를 Git 원격 저장소에 연결하고, 코드를 커밋한 뒤 푸시하는 절차입니다.

> 아래 명령어의 폴더 경로, 사용자 이름, 이메일, 저장소 주소는 본인 정보로 바꿔 입력하세요. Git과 Visual Studio Code가 설치되어 있어야 합니다.

## 1. 로컬 PC에 작업 폴더 만들기

원하는 위치에 프로젝트 작업 폴더를 만들고 이동합니다. 아래는 Windows PowerShell 기준 예시입니다.

```powershell
mkdir my-project
cd my-project
```

기존 프로젝트가 있다면 해당 폴더로 이동하면 됩니다.

## 2. Git 원격 저장소 만들기

GitHub 등 Git 호스팅 서비스에서 새 저장소를 생성합니다.

1. 로그인 후 **New repository**를 선택합니다.
2. 저장소 이름과 공개 범위(Public 또는 Private)를 설정합니다.
3. 빈 저장소로 생성합니다. 로컬 프로젝트를 처음 올리는 경우 README, .gitignore, License 자동 생성 옵션은 선택하지 않습니다.
4. 생성된 저장소의 HTTPS 주소를 복사합니다.

저장소 주소 예시:

```text
https://github.com/your-account/my-project.git
```

## 3. VS Code에서 작업 폴더 열기

VS Code의 **파일 → 폴더 열기**에서 1단계의 작업 폴더를 선택합니다.

또는 작업 폴더의 터미널에서 다음 명령어를 실행합니다.

```powershell
code .
```

VS Code에서 **터미널 → 새 터미널**을 열고, 현재 경로가 프로젝트 폴더인지 확인합니다. 이후 명령어는 이 폴더에서 실행합니다.

## 4. Git 사용자 이름과 이메일 설정하기

커밋에 기록할 작성자 정보를 설정합니다. 이 정보는 원격 저장소 로그인 정보와 별개입니다.

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

- `--global`: 현재 PC 사용자 계정의 모든 Git 저장소에 적용합니다.
- 이 프로젝트에만 적용하려면 5단계 실행 후 `--global`을 빼고 설정합니다.
- GitHub 계정에 커밋을 연결하려면 해당 계정에 등록된 이메일 또는 GitHub에서 제공하는 비공개 이메일을 사용합니다.

설정 확인:

```powershell
git config --global user.name
git config --global user.email
```

## 5. Git 저장소 초기화하기

작업 폴더를 Git 저장소로 초기화합니다.

```powershell
git init
```

작업 폴더에 `.git` 폴더가 생성되고 Git으로 변경 사항을 관리할 수 있게 됩니다.

## 6. 브랜치 이름을 Main으로 변경하기

현재 브랜치 이름을 `Main`으로 지정합니다.

```powershell
git branch -M Main
```

> 브랜치 이름은 대소문자를 구분합니다. 이 문서는 요청한 `Main`으로 통일했습니다. `main`을 사용하려면 이후 명령어에서도 동일하게 바꿔 입력하세요.

## 7. 원격 저장소 연결하기

2단계에서 복사한 원격 저장소 주소를 `origin`이라는 이름으로 등록합니다.

```powershell
git remote add origin https://github.com/your-account/my-project.git
```

연결된 주소를 확인합니다.

```powershell
git remote -v
```

이미 `origin`이 등록되어 있다면 주소를 확인한 뒤, 변경이 필요한 경우 다음 명령어를 사용합니다.

```powershell
git remote set-url origin https://github.com/your-account/my-project.git
```

## 8. 코드 커밋하기

작업 폴더에 업로드할 코드를 저장합니다. 업로드에서 제외할 파일은 먼저 `.gitignore`에 작성합니다. 비밀번호, 인증 토큰, `.env` 등 민감한 파일이 포함되지 않도록 확인하세요.

현재 변경 사항을 확인합니다.

```powershell
git status
```

현재 폴더와 하위 폴더의 변경 사항을 스테이징하고, 커밋할 내용을 확인한 뒤 커밋합니다.

```powershell
git add .
git diff --cached
git commit -m "Initial commit"
```

- `git add .`: 변경 사항을 커밋 대상으로 등록합니다.
- `git diff --cached`: 커밋 대상의 변경 내용을 확인합니다.
- `git commit`: 로컬 저장소에 변경 이력을 저장합니다.

## 9. 원격 저장소에 푸시하기

로컬의 `Main` 브랜치를 원격 저장소에 업로드합니다.

```powershell
git push -u origin Main
```

`-u`는 로컬 브랜치와 원격 브랜치의 추적 관계를 설정합니다. 처음 푸시할 때 인증 화면이 나타나면 해당 서비스의 안내에 따라 로그인합니다.

푸시가 완료되면 원격 저장소 페이지를 새로고침하여 `Main` 브랜치에 코드가 올라갔는지 확인합니다.

> 원격 저장소에 이미 커밋이 있으면 푸시가 거절될 수 있습니다. 이 경우 원격 변경 사항을 확인하고 로컬 작업과 통합한 뒤 다시 푸시하세요.

## 이후 코드를 수정했을 때

변경 사항을 확인하고 커밋한 뒤 푸시합니다. 첫 푸시에서 추적 관계를 설정했으므로 이후에는 `git push`만 사용하면 됩니다.

```powershell
git status
git add .
git diff --cached
git commit -m "변경 내용 설명"
git push
```
