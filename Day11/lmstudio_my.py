#pip install openai
from openai import OpenAI
#lm studio에 로컬 서버 연결
client=OpenAI(
    base_url='http://localhost:1235/v1',
    api_key='lm-studio'
)

models=client.models.list()
if not models.data:
    raise RuntimeError('사용가능한 모델이 없습니다.')
model_id=models.data[0].id
print(f'사용모델 : {model_id}')