import streamlit as st

from color_utils import render_swatches, rgb_to_hex, theme_from_color


st.set_page_config(page_title="RGB 컬러 픽커", page_icon="🎛️", layout="wide")
st.title("RGB 컬러 픽커")
st.write("RGB 채널을 움직여 색상 테마를 조정하세요.")

initial_color = st.session_state.get("selected_color", "#D85D45")
initial_rgb = tuple(int(initial_color[index : index + 2], 16) for index in (1, 3, 5))
for channel, value in zip(("red", "green", "blue"), initial_rgb):
    if channel not in st.session_state:
        st.session_state[channel] = value

controls, preview = st.columns([1, 1.5], gap="large")
with controls:
    red = st.slider("Red", 0, 255, key="red")
    green = st.slider("Green", 0, 255, key="green")
    blue = st.slider("Blue", 0, 255, key="blue")

color = rgb_to_hex(red, green, blue)
st.session_state.selected_color = color
with preview:
    st.subheader("컬러 테마")
    st.markdown(render_swatches(theme_from_color(color)), unsafe_allow_html=True)
    st.code(f"RGB  {red}, {green}, {blue}    HEX  {color}")