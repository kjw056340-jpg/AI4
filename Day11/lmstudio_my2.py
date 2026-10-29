from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

BASE_URL = "http://localhost:1235/v1"
API_KEY = "lm-studio"  # 서버 인증을 켰다면 실제 LM Studio 토큰으로 변경

SYSTEM_PROMPT = "당신은 친절한 AI 도우미입니다. 한국어로 답변하세요."


def select_model(client):
    """서버에서 모델 목록을 가져와 사용자가 선택합니다."""
    models = client.models.list().data

    if not models:
        raise RuntimeError(
            "사용 가능한 모델이 없습니다. LM Studio에서 채팅 모델을 로드하세요."
        )

    print("\n사용 가능한 모델")
    for number, model in enumerate(models, start=1):
        print(f"  {number}. {model.id}")

    while True:
        value = input("\n채팅 모델 번호를 선택하세요: ").strip()

        if value.isdigit() and 1 <= int(value) <= len(models):
            return models[int(value) - 1].id

        print("목록에 있는 번호를 입력하세요.")


def chat(client, model_id):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"\n사용 모델: {model_id}")
    print("종료: /exit | 대화 초기화: /clear")
    print("-" * 50)

    while True:
        user_input = input("\n나: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "종료"):
            print("채팅을 종료합니다.")
            break

        if user_input.lower() == "/clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("대화 기록을 초기화했습니다.")
            continue

        # 요청이 성공한 경우에만 대화 기록에 추가합니다.
        request_messages = messages + [
            {"role": "user", "content": user_input}
        ]

        print("\nAI: ", end="", flush=True)

        try:
            answer_parts = []
            finish_reason = None

            # stream=True: 생성되는 답변을 조금씩 받아 출력합니다.
            with client.chat.completions.create(
                model=model_id,
                messages=request_messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            ) as stream:
                for chunk in stream:
                    if not chunk.choices:
                        continue

                    choice = chunk.choices[0]
                    content = choice.delta.content

                    if content:
                        print(content, end="", flush=True)
                        answer_parts.append(content)

                    if choice.finish_reason:
                        finish_reason = choice.finish_reason

            print()

            answer = "".join(answer_parts)
            if not answer.strip():
                print("텍스트 응답이 없습니다. 모델과 서버 로그를 확인하세요.")
                continue

            messages = request_messages + [
                {"role": "assistant", "content": answer}
            ]

            if finish_reason == "length":
                print("[출력 한도에 도달해 답변이 잘렸습니다.]")

        except APITimeoutError:
            print("\n응답 시간이 초과되었습니다. 잠시 후 다시 시도하세요.")

        except APIConnectionError:
            print(f"\n서버에 연결할 수 없습니다: {BASE_URL}")
            print("LM Studio 서버 실행 여부와 포트 번호를 확인하세요.")

        except APIStatusError as error:
            print(f"\n서버 오류 ({error.status_code}): {error}")
            print("모델 로드 상태와 LM Studio 서버 로그를 확인하세요.")
            print("대화가 너무 길다면 /clear를 입력하세요.")


def main():
    try:
        with OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            timeout=180.0,
            max_retries=0,
        ) as client:
            model_id = select_model(client)
            chat(client, model_id)

    except APITimeoutError:
        print("모델 목록을 가져오는 시간이 초과되었습니다.")

    except APIConnectionError:
        print(f"LM Studio 서버에 연결할 수 없습니다: {BASE_URL}")
        print("Developer에서 서버를 시작하고 포트 번호를 확인하세요.")

    except APIStatusError as error:
        print(f"서버 오류 ({error.status_code}): {error}")

    except RuntimeError as error:
        print(error)

    except (KeyboardInterrupt, EOFError):
        print("\n채팅을 종료합니다.")


if __name__ == "__main__":
    main()