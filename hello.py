from datetime import datetime
from random import choice
from zoneinfo import ZoneInfo

import streamlit as st


st.title("인사말 앱")

name = st.text_input("이름을 입력하세요")

if name:
    st.write(f"안녕하세요, {name}님! 만나서 반가워요.")

if st.button("현재 시간 보기"):
    current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime(
        "%Y년 %m월 %d일 %H시 %M분 %S초"
    )
    st.write(f"현재 시간은 {current_time}입니다.")

if st.button("오늘의 운세 받기"):
    fortunes = [
        "오늘은 좋은 일이 가득한 하루가 될 거예요!",
        "새로운 기회가 찾아오는 날이에요. 자신 있게 도전해 보세요!",
        "작은 행운이 큰 기쁨으로 이어지는 하루예요!",
        "떨어지는 낙엽도 조심하세요 온세상이 너를 저주하는 날이에요!",
        "오늘은 충분히 잘하고 있어요. 자신을 믿어 보세요!",
    ]
    st.write(f"오늘의 운세: {choice(fortunes)}")
