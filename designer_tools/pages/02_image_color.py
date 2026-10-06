import streamlit as st
from PIL import Image

from color_utils import extract_top_colors, render_swatches, theme_from_color


st.set_page_config(page_title="이미지 컬러 분석", page_icon="🖼️", layout="wide")
st.title("이미지 컬러 분석")
st.write("이미지에서 주요 색상 5개를 추출해 컬러 테마를 구성합니다.")

uploaded_image = st.file_uploader(
    "이미지 선택", type=("png", "jpg", "jpeg", "webp")
)

if uploaded_image:
    image = Image.open(uploaded_image)
    palette = extract_top_colors(image)
    image_column, palette_column = st.columns([1, 1.3], gap="large")
    with image_column:
        st.image(image, caption=uploaded_image.name, use_container_width=True)
    with palette_column:
        st.subheader("추출된 주요 색상")
        total_pixels = sum(count for _, count in palette)
        swatches = {
            f"색상 {index} · {count / total_pixels:.0%}": color
            for index, (color, count) in enumerate(palette, start=1)
        }
        st.markdown(render_swatches(swatches), unsafe_allow_html=True)

        st.subheader("컬러 테마")
        st.markdown(
            render_swatches(theme_from_color(palette[0][0])),
            unsafe_allow_html=True,
        )
else:
    st.info("PNG, JPG, JPEG 또는 WebP 이미지를 선택해 주세요.")