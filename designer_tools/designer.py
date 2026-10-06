import streamlit as st


st.set_page_config(page_title="디자이너 색상 도구", page_icon="🎨", layout="wide")

st.title("디자이너 색상 도구")
st.write("색을 고르고 이미지에서 팔레트를 찾은 뒤, 필터로 마무리하세요.")

apps = [
    (
        "01",
        "RGB 컬러 픽커",
        "RGB 채널을 조정해 기본색·보조색·배경색 테마를 만듭니다.",
        "pages/01_color_picker.py",
        ":material/palette:",
    ),
    (
        "02",
        "이미지 컬러 분석",
        "이미지에서 가장 눈에 띄는 색상 5개를 추출합니다.",
        "pages/02_image_color.py",
        ":material/image_search:",
    ),
    (
        "03",
        "이미지 필터",
        "흑백, 세피아, 블러 효과를 적용하고 결과를 저장합니다.",
        "pages/03_image_filter.py",
        ":material/photo_filter:",
    ),
]

st.subheader("앱 선택")
columns = st.columns(3, gap="medium")
for column, (number, title, description, page, icon) in zip(columns, apps):
    with column:
        with st.container(border=True):
            st.caption(f"COLOR TOOLS  /  {number}")
            st.markdown(f"### {title}")
            st.write(description)
            st.page_link(page, label="열기", icon=icon, use_container_width=True)