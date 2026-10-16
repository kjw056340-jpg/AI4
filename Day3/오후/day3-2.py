# class promptEmptyError(Exception):
#     pass

# prompt= ""
# try:
#     print(1/0)

#     if not prompt.strip():
#         raise promptEmptyError()
    

# except Exception as e:
#     print('프롬프트는 반드시 제공되어야 합니다.')
# except ZeroDivisionError as e:
#     print('0으로 나눌 수 없습니다.')

# print('정상종료')


class AIServiceError(Exception):
    """AI 서비스 최상위 기본 예외 클래스"""
    pass
class PromptEmptyError(AIServiceError):
    """프롬프트가 비어있을 때 발생하는 예외"""
    pass
class TokenQuotaExceededError(AIServiceError):
    """토큰 한도 초과 시 요청량과 잔여 한도 컨텍스트를 함께 전달하는 예외"""
    def __init__(self, requested: int, remaining: int):
        self.requested = requested
        self.remaining = remaining
        super().__init__(f"토큰 한도 초과! (요청: {requested}개, 잔여 한도: {remaining}개)")
class CodexClient:
    def __init__(self, daily_quota: int = 100):
        self.remaining_tokens = daily_quota

    def generate_code(self, prompt: str, estimated_tokens: int) -> str:
        if not prompt.strip():
            raise PromptEmptyError("프롬프트에 최소 1글자 이상의 명령어를 입력해주세요.")
        if estimated_tokens > self.remaining_tokens:
            raise TokenQuotaExceededError(estimated_tokens, self.remaining_tokens)
        self.remaining_tokens -= estimated_tokens
        return f"[생성 성공] '{prompt}' 코드 생성 완료 (남은 토큰: {self.remaining_tokens})"
client = CodexClient(daily_quota=50)
test_requests = [
    ("클래스 리팩토링 코드 작성", 30),
    ("   ", 10),
    ("대규모 프로젝트 전체 변환", 40),]
for prompt_text, tokens in test_requests:
    try:
        result = client.generate_code(prompt_text, tokens)
        print(result)
    except PromptEmptyError as e:
        print(f"[입력 검증 실패] {e}")
    except TokenQuotaExceededError as e:
        print(f"[쿼터 경보] {e} -> 기본 요금제를 업그레이드하거나 요청 길이를 줄이세요.")