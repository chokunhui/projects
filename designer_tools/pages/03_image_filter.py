import io

import streamlit as st
from PIL import Image, ImageFilter, ImageOps


st.set_page_config(page_title="이미지 필터", page_icon="🪄", layout="wide")
st.title("이미지 필터")
st.write("필터를 조합해 이미지를 다듬고 PNG로 다운로드하세요.")

uploaded_image = st.file_uploader(
    "이미지 선택", type=("png", "jpg", "jpeg", "webp")
)

if uploaded_image:
    source = ImageOps.exif_transpose(Image.open(uploaded_image)).convert("RGB")
    controls, preview = st.columns([1, 1.5], gap="large")
    with controls:
        selected_filters = st.multiselect(
            "적용할 필터", ("흑백", "세피아", "블러"), default=[]
        )
        blur_radius = st.slider("블러 강도", 1, 20, 5, disabled="블러" not in selected_filters)

    filtered = source
    if "흑백" in selected_filters:
        filtered = ImageOps.grayscale(filtered).convert("RGB")
    if "세피아" in selected_filters:
        grayscale = ImageOps.grayscale(filtered)
        filtered = ImageOps.colorize(
            grayscale, black="#38251B", white="#F2D8A7"
        ).convert("RGB")
    if "블러" in selected_filters:
        filtered = filtered.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    with preview:
        st.image(filtered, caption="필터 미리보기", use_container_width=True)
        image_buffer = io.BytesIO()
        filtered.save(image_buffer, format="PNG")
        st.download_button(
            "결과 이미지 다운로드",
            data=image_buffer.getvalue(),
            file_name="filtered-image.png",
            mime="image/png",
            icon=":material/download:",
            use_container_width=True,
        )
else:
    st.info("PNG, JPG, JPEG 또는 WebP 이미지를 선택해 주세요.")