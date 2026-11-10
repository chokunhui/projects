from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent / "data" / "cleaned_pension.csv"
PENSION_RATE = 0.095
SALARY_CAP = 6_590_000


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


st.set_page_config(
    page_title="📋 국민연금 사업장 분석 대시보드",
    layout="wide",
)
st.title("📋 국민연금 사업장 분석 대시보드")

if not DATA_PATH.is_file():
    st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
    st.stop()

try:
    df = load_data()
except (OSError, UnicodeDecodeError, pd.errors.ParserError) as exc:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {exc}")
    st.stop()

required_columns = [
    "sido",
    "member_count",
    "estimated_salary_per",
    "company_type",
]
missing_columns = [column for column in required_columns if column not in df.columns]
if missing_columns:
    st.error("필수 컬럼이 없습니다: " + ", ".join(missing_columns))
    st.stop()

with st.sidebar:
    st.subheader("지역 선택")
    sido_options = sorted(df["sido"].dropna().unique().tolist())
    selected_sido = st.selectbox("시도", options=sido_options)

    st.subheader("분석 필터")
    selected_company_type = st.selectbox(
        "사업장 형태",
        options=["전체", "법인", "개인"],
    )
    minimum_member_count = st.slider(
        "최소 가입자 수",
        min_value=1,
        max_value=100,
        value=1,
    )

st.subheader("전국 요약")
metric_columns = st.columns(4)
metric_columns[0].metric("총 등록 사업장 수", f"{len(df):,}")
metric_columns[1].metric(
    "총 가입자 수",
    f"{df['member_count'].sum():,.0f}",
)
metric_columns[2].metric(
    "전국 평균 1인당 추정 월급여",
    f"{df['estimated_salary_per'].mean():,.0f}원",
)

if "year_month" in df.columns and df["year_month"].notna().any():
    latest_year_month = df["year_month"].dropna().max()
    if isinstance(latest_year_month, pd.Timestamp):
        latest_year_month = latest_year_month.strftime("%Y-%m")
    metric_columns[3].metric("데이터 기준 연월", str(latest_year_month))
elif "year_month" not in df.columns:
    metric_columns[3].metric("데이터 기준 연월", "컬럼 없음")
    st.warning(
        "cleaned_pension.csv에 year_month 컬럼이 없어 기준 연월을 표시할 수 없습니다."
    )
else:
    metric_columns[3].metric("데이터 기준 연월", "데이터 없음")
