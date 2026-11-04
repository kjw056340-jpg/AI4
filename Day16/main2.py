import os
from dotenv import load_dotenv

import requests
import streamlit as st

load_dotenv(override=True)
base_url = os.getenv('LLAMA_BASE_URL','').strip()
model = os.getenv('LLAMA_MODEL','').strip()
timeout_text = os.getenv('LLAMA_TIMEOUT_SECONDS',"180").strip()
timeout_seconds = int(timeout_text)

name = st.text_input('이름')
question = st.text_input('질문')

with st.chat_message('user'):
    st.text(f"{name} : {question}")

import requests


def ask_llm(base_url, model, question, timeout_seconds=120):

    # API 주소
    endpoint = f"{base_url}/v1/chat/completions"

    # 요청 헤더
    headers = {
        "Content-Type": "application/json"
    }

    # 시스템 프롬프트
    system_prompt = """
당신은 한국어 전문 AI 도우미입니다.

[기본 역할]
- 사용자의 질문에 정확하고 직접적으로 답변합니다.
- 쉽고 자연스러운 한국어를 사용합니다.

[답변 규칙]
1. 반드시 한국어로 답변합니다.
2. 질문의 핵심에 집중합니다.
3. 질문과 관계없는 내용을 추가하지 않습니다.
4. 모르는 내용은 추측하지 말고 모른다고 답변합니다.
5. 동일한 단어나 문장, 표현을 반복하지 않습니다.
6. 불필요한 인사말과 자기소개는 생략합니다.
7. 기본적으로 3~5문장 이내로 답변합니다.
8. 코드 질문에는 실행 가능한 코드와 핵심 설명을 제공합니다.
9. 답변을 완료하면 즉시 종료합니다.

[주의사항]
- 의미 없는 문장이나 단어를 반복하지 마세요.
- 질문을 그대로 반복하지 마세요.
- 확실하지 않은 정보를 사실처럼 작성하지 마세요.
"""

    # 메시지 구성
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # API 요청 데이터
    payload = {
        "model": model,

        "messages": messages,

        # 생성 설정
        "temperature": 0.3,
        "top_p": 0.85,
        "top_k": 20,

        # 반복 방지
        "repeat_penalty": 1.1,
        "presence_penalty": 0.5,
        "frequency_penalty": 0.3,

        # 최대 출력 토큰
        "max_tokens": 256,

        # Thinking 비활성화 (지원 버전에서 적용)
        "chat_template_kwargs": {
            "enable_thinking": False
        },

        # 스트리밍 비활성화
        "stream": False
    }

    try:

        with requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=(5, timeout_seconds)
        ) as response:

            response.raise_for_status()

            # JSON 응답 변환
            data = response.json()

            # 응답 내용 추출
            answer = data["choices"][0]["message"]["content"]

            if not answer or not answer.strip():
                return "답변을 생성하지 못했습니다. 다시 질문해 주세요."

            return answer.strip()

    except requests.exceptions.Timeout:
        return "AI 서버 응답 시간이 초과되었습니다."

    except requests.exceptions.ConnectionError:
        return "AI 서버에 연결할 수 없습니다."

    except requests.exceptions.HTTPError as e:
        return f"AI 서버 HTTP 오류: {e}"

    except (KeyError, IndexError, TypeError):
        return "AI 서버의 응답 형식이 올바르지 않습니다."

    except requests.exceptions.RequestException as e:
        return f"API 요청 오류: {e}"

    except Exception as e:
        return f"예상하지 못한 오류: {e}"


if st.button('ai 답변 받기'):
    headers={}
    with st.spinner('ai가 답변을 생성하고 있습니다.'):
        answer = ask_llm(
            base_url=base_url,
            model=model,
            question=question,
            timeout_seconds=timeout_seconds
        )       
        
        with st.chat_message('assistant'):
            st.text(answer.strip())