# streamlit의 세션 메세지를 유지하고 재실행할때마다 다시 출력
import streamlit as st

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

with st.sidebar:
    st.header('대화설정')
    title = st.text_input(
        '대화 제목', value='FastAPI 대화 실습'
    )
    style = st.selectbox(
        '모의 답변 형식',
        ['간단히','단계별']
    )
    st.caption('제목을 바꿔도 현재 대화 기록을 유지합니다.')
st.title('대화화면 프로토 타입')    
st.caption('현재 세션의 대화 기록을 유지합니다 DB에는 저장하지 않습니다.')

for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.text(message['content'])

prompt = st.chat_input('메세지를 입력하세요')
if prompt is not None:
    content = prompt.strip()
    title_clean = title.strip()
    if style =='간단히':
        answer = f'모의답변: {content}  \n 내용을 확인했습니다.' 
    else:
        answer = f'1.메세지 확인: {content}\n2. 실제 답변 생성 전 입니다.' 
    st.session_state['messages'].append({'role':'user', 'content':content})
    st.session_state['messages'].append({'role':'assistant', 'content':answer})
    with st.chat_message('user'):
        st.text(content)
    with st.chat_message('assistant'):
        st.text(answer)