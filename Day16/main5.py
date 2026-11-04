"""Streamlit에서 기존 FastAPI·Supabase PostgreSQL·Redis를 실제 호출한다."""
import os  # 외부 서비스 주소를 조회한다
from uuid import uuid4  # 메시지 저장 요청을 식별한다

import requests  # 별도 프로세스인 FastAPI·LLM 서버와 HTTP 통신한다
import streamlit as st  # UI와 현재 연결의 식별자·미처리 작업 보관
from dotenv import load_dotenv

# 현재 차시 폴더의 설정. 기존 프로세스 환경변수가 우선이며 ${...}를 치환하지 않는다.
load_dotenv(".env", override=False, interpolate=False)
API_BASE_URL = os.getenv("API_BASE_URL", "").strip().rstrip("/")


def request_json(method, url, payload=None, session_id=None, read_timeout=15, api_key=""):
    """요청 한 번을 전송한다. 실패를 모의 응답이나 빈 기록으로 바꾸지 않는다."""
    headers = {}
    if session_id:
        headers["X-Session-Id"] = session_id  # FastAPI가 Redis에서 대화방을 찾는 데 사용
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key}"
    with requests.request(
        method, url,  # 호출자가 지정한 HTTP 메서드와 전체 주소
        json=payload,  # POST 딕셔너리를 JSON으로 인코딩. GET에는 None
        headers=headers,  # 세션 또는 모델 인증 헤더
        timeout=(5, read_timeout),  # 연결 5초·읽기 대기. 전체 작업 시간 상한은 아님
    ) as response:
        response.raise_for_status()  # 4xx/5xx를 호출자에 전달
        return response.json()  # JSON을 Python 자료형으로 복원


def api(method, path, payload=None, session_id=None):
    return request_json(method, API_BASE_URL + path, payload, session_id)


st.title("하이브리드 대화 서비스")
if not API_BASE_URL:
    st.error("API_BASE_URL을 .env 또는 환경변수에 설정하세요.")
    st.stop()
# 화면에는 식별자와 조회 결과를 보관한다. 메시지 원본은 Supabase DB에 있다.
for key, value in [("room_id", None), ("session_id", None), ("rows", [])]:
    if key not in st.session_state:
        st.session_state[key] = value

try:
    # 실제 DB 대화방 목록이다. 연결 오류를 빈 목록으로 처리하지 않는다.
    rooms = api("GET", "/conversations")
    room_map = {f"{r['title']} | {r['id']}": r["id"] for r in rooms}
    with st.sidebar:
        st.header("대화방")
        title = st.text_input("새 대화 제목", value="Streamlit 연동 실습")
        # 새 대화 생성은 DB 행과 Redis 세션을 순서대로 만든다.
        if st.button("새 대화 만들기"):
            if not title.strip():
                st.warning("대화 제목을 입력하세요.")
            else:
                room = api("POST", "/conversations", {"title": title.strip()})
                session = api("POST", "/sessions", {"conversation_id": room["id"]})
                # DB 생성과 Redis 발급이 모두 성공한 뒤 연결 상태를 함께 바꾼다.
                st.session_state["room_id"] = room["id"]
                st.session_state["session_id"] = session["session_id"]
                st.session_state["rows"] = []
                st.rerun()  # 새 대화방을 목록과 본문에 반영
        chosen = st.selectbox("저장된 대화방", list(room_map), index=None,
                              placeholder="대화방 선택")  # 미선택은 None, 선택값은 표시 문자열
        if st.button("선택한 대화 연결", disabled=chosen is None):
            room_id = room_map[chosen]
            session = api("POST", "/sessions", {"conversation_id": room_id})
            st.session_state["room_id"] = room_id
            st.session_state["session_id"] = session["session_id"]
            st.rerun()  # 새 세션으로 DB 기록을 다시 읽는다
        st.caption(f"현재 대화 ID: {st.session_state['room_id'] or '선택 전'}")

    sid = st.session_state["session_id"]
    if sid:
        st.session_state["rows"] = api("GET", "/messages", session_id=sid)
    for row in st.session_state["rows"]:
        with st.chat_message("user"):  # 이전 백엔드에는 role이 없으며 이 차시는 사용자 메모만 저장
            st.text(row["content"])
    st.caption(f"DB에서 조회한 메시지: {len(st.session_state['rows'])}개")

    prompt = st.chat_input("메시지를 입력하세요.", disabled=sid is None)
    if prompt is not None:
        content = prompt.strip()
        if not content or len(content) > 500:
            st.warning("메시지는 양끝 공백을 정리한 뒤 1~500자로 입력하세요.")
        else:
            api("POST", "/messages", {"content": content, "request_id": str(uuid4())}, session_id=sid)
            st.rerun()  # 로컬 append 대신 DB 재조회로 결과를 출력
except requests.exceptions.HTTPError as exc:
    code = exc.response.status_code if exc.response is not None else 0
    if code == 401:
        st.error("세션이 없거나 만료되었습니다. 같은 대화방에 다시 연결/복원하세요. DB 기록은 삭제되지 않았습니다.")
    elif code == 409:
        st.error("같은 요청 ID의 내용이 다릅니다. 미처리 내용을 바꾸지 말고 원본 요청을 확인하세요.")
    else:
        st.error(f"서버 HTTP {code} 오류입니다. API·DB·Redis·모델 로그를 확인하세요.")
except requests.exceptions.Timeout:
    st.error("요청 대기 시간 초과입니다. 서버 처리가 완료됐을 수 있으므로 저장 결과를 먼저 확인하세요.")
except requests.exceptions.RequestException:
    st.error("서버 연결 또는 JSON 응답 오류입니다. 실행 중인 서버와 .env 주소를 확인하세요.")
except (KeyError, IndexError, TypeError):
    st.error("API 응답 구조가 예상과 다릅니다. 지정한 백엔드 버전·role 마이그레이션을 확인하세요.")
except ValueError as exc:
    st.error(str(exc))  # 코드에서 작성한 설정/답변 검증 문구만 사용