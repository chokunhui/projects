import os
import json
import calendar
from datetime import date

import pandas as pd
import streamlit as st


DIARY_FILE = "diary.csv"
SETTINGS_FILE = "settings.json"
DIARY_COLUMNS = ["날짜", "작성자", "제목", "내용", "날씨", "기분", "음식"]
THEME_COLORS = {
    "파랑": "#2563eb",
    "초록": "#15803d",
    "보라": "#7c3aed",
    "주황": "#ea580c",
    "빨강": "#dc2626",
}


def load_settings():
    defaults = {"author": "", "theme": "파랑"}
    if not os.path.exists(SETTINGS_FILE):
        return defaults

    try:
        with open(SETTINGS_FILE, encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        return defaults

    if not isinstance(settings, dict):
        return defaults
    return {**defaults, **settings}


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, ensure_ascii=False, indent=2)


def load_diaries():
    if not os.path.exists(DIARY_FILE):
        return pd.DataFrame(columns=DIARY_COLUMNS)

    try:
        diaries = pd.read_csv(DIARY_FILE, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=DIARY_COLUMNS)

    for column in DIARY_COLUMNS:
        if column not in diaries.columns:
            diaries[column] = ""
    return diaries[DIARY_COLUMNS].reset_index(drop=True)


def save_diaries(diaries):
    diaries[DIARY_COLUMNS].to_csv(DIARY_FILE, index=False, encoding="utf-8-sig")


def previous_month(month):
    if month.month == 1:
        return month.replace(year=month.year - 1, month=12)
    return month.replace(month=month.month - 1)


def next_month(month):
    if month.month == 12:
        return month.replace(year=month.year + 1, month=1)
    return month.replace(month=month.month + 1)


settings = load_settings()
last_viewed_date = settings.get("last_viewed_date")
today = date.today().strftime("%Y-%m-%d")
settings["last_viewed_date"] = today
save_settings(settings)

with st.sidebar:
    st.header("설정")
    author = st.text_input("작성자 이름", value=settings.get("author", ""))
    if st.button("저장", key="save_settings"):
        settings["author"] = author
        save_settings(settings)
        st.success("설정이 저장되었습니다!")

    theme_options = list(THEME_COLORS)
    saved_theme = settings.get("theme", "파랑")
    theme_index = (
        theme_options.index(saved_theme) if saved_theme in theme_options else 0
    )
    theme = st.selectbox("테마 색상", theme_options, index=theme_index)
    if theme != settings.get("theme"):
        settings["theme"] = theme
        save_settings(settings)

st.markdown(
    f'<div style="background-color: {THEME_COLORS[theme]}; color: white; '
    'padding: 12px 16px; border-radius: 6px;">'
    f'오늘의 테마: {theme}</div>',
    unsafe_allow_html=True,
)

st.title("📔 나의 일기장")

title = st.text_input("제목")
content = st.text_area("내용", height=150)
weather = st.selectbox("오늘의 날씨", ["맑음", "흐림", "비", "눈", "바람"])
mood = st.selectbox(
    "오늘의 기분", ["아주 좋음", "좋음", "보통", "나쁨", "아주 나쁨"]
)
food = st.text_input("오늘 먹은 음식", placeholder="예: 김치찌개, 샐러드")

if st.button("일기 저장", key="save_diary"):
    new_diary = pd.DataFrame(
        [
            {
                "날짜": date.today().strftime("%Y-%m-%d"),
                "작성자": author,
                "제목": title,
                "내용": content,
                "날씨": weather,
                "기분": mood,
                "음식": food,
            }
        ]
    )
    diaries = pd.concat([load_diaries(), new_diary], ignore_index=True)
    save_diaries(diaries)
    st.success("일기가 저장되었습니다!")

diaries = load_diaries()

st.subheader("기록 달력")
if "calendar_month" not in st.session_state:
    current_date = date.today()
    st.session_state.calendar_month = current_date.replace(day=1)

calendar_controls = st.columns([1, 3, 1])
with calendar_controls[0]:
    if st.button("◀ 이전 달", key="previous_month"):
        st.session_state.calendar_month = previous_month(
            st.session_state.calendar_month
        )
        st.rerun()
with calendar_controls[1]:
    st.markdown(
        f"<h3 style='text-align: center'>{st.session_state.calendar_month.year}년 "
        f"{st.session_state.calendar_month.month}월</h3>",
        unsafe_allow_html=True,
    )
with calendar_controls[2]:
    if st.button("다음 달 ▶", key="next_month"):
        st.session_state.calendar_month = next_month(
            st.session_state.calendar_month
        )
        st.rerun()

weekday_columns = st.columns(7)
for column, weekday in zip(
    weekday_columns, ["월", "화", "수", "목", "금", "토", "일"]
):
    column.markdown(f"**{weekday}**")

daily_counts = {}
if not diaries.empty:
    diary_dates = pd.to_datetime(
        diaries["날짜"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    daily_counts = diary_dates.dropna().value_counts().to_dict()

month = st.session_state.calendar_month
for week in calendar.monthcalendar(month.year, month.month):
    day_columns = st.columns(7)
    for column, day in zip(day_columns, week):
        with column:
            if day:
                date_key = f"{month.year:04d}-{month.month:02d}-{day:02d}"
                st.markdown(f"**{day}일**")
                st.caption(f"{daily_counts.get(date_key, 0)}건")
            else:
                st.write("")

st.subheader("저장된 일기")
if diaries.empty:
    st.write("아직 작성된 일기가 없어요.")
else:
    for row_index, diary in diaries.iterrows():
        diary_columns = st.columns([8, 1])
        with diary_columns[0]:
            st.markdown(f"**{diary['날짜']} · {diary['제목']}**")
            st.caption(
                f"작성자: {diary['작성자']} | 날씨: {diary['날씨']} | "
                f"기분: {diary['기분']} | 먹은 음식: {diary['음식']}"
            )
            st.write(diary["내용"])
        with diary_columns[1]:
            if st.button("삭제", key=f"delete_diary_{row_index}"):
                diaries = diaries.drop(index=row_index).reset_index(drop=True)
                save_diaries(diaries)
                st.rerun()

if last_viewed_date:
    st.caption(f"마지막으로 일기를 확인한 날: {today}")
else:
    st.write("처음 방문이에요! 일기를 써봐요 🌱")
