import streamlit as st
with st.sidebar:
    st.header('대화설정')
    title = st.text_input('대화제목',value='FastAPI 대화 실습')
    style = st.selectbox(
        '모의 답변 형식',
        ['간단히','단계별']
    )

st.title('대화화면 프로토타입')    
st.caption('대화 제목과 메세지를 배치하고 모의 응답을 확인합니다.')

intpu_col, preview_col =  st.columns([1,2])
with intpu_col:
    st.subheader('메세지 작성')
    messages = st.text_area('메세지',placeholder="예) 대화이력을 저장하는 이유는?")
    st.caption(f"선택한 형식:{style}")
    preview = st.button('대화미리보기')

with preview_col:
    st.subheader(title.strip() or "제목없음")
    if preview:
        clean_title = title.strip()
        content = messages.strip()
        if style =='간단히':
            answer = f'모의답변: {content}  \n 내용을 확인했습니다.' 
        else:
            answer = f'1.메세지 확인: {content}\n2. 실제 답변 생성 전 입니다.' 
        with st.chat_message('user'):
            st.text(content)
        with st.chat_message('assistant'):
            st.text(answer)