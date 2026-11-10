import os

import pandas as pd
import streamlit as st


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "pension_raw.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_pension.csv")


@st.cache_data
def load_csv(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path, encoding="cp949", low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="utf-8-sig", low_memory=False)


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(
            "원본 CSV에 다음 필수 컬럼이 없습니다: " + ", ".join(missing)
        )


def preview(df: pd.DataFrame) -> None:
    st.dataframe(df.head(), use_container_width=True)


st.set_page_config(page_title="국민연금 사업장 데이터 전처리", layout="wide")
st.title("📋 국민연금 사업장 데이터 전처리")

if not os.path.exists(RAW_DATA_PATH):
    st.error(f"원본 CSV 파일을 찾을 수 없습니다: {RAW_DATA_PATH}")
    st.stop()

try:
    raw_df = load_csv(RAW_DATA_PATH)
except Exception as exc:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {exc}")
    st.stop()

before_count = len(raw_df)

raw_company_name = "사업장명"
raw_status = "사업장가입상태코드 1 등록 2 탈퇴"
raw_address = "사업장도로명상세주소"
raw_sido_code = "법정동주소광역시도코드"
raw_type = "사업장형태구분코드 1 법인 2 개인"
raw_industry = "사업장업종코드명"
raw_members = "가입자수"
raw_charge = "당월고지금액"
raw_new_members = "신규취득자수"
raw_lost_members = "상실가입자수"

raw_required_columns = [
    raw_company_name,
    raw_status,
    raw_address,
    raw_sido_code,
    raw_type,
    raw_industry,
    raw_members,
    raw_charge,
    raw_new_members,
    raw_lost_members,
]

st.subheader("전처리 전/후 행 수")
metric_before, metric_after = st.columns(2)
metric_before.metric("전처리 전 행 수", f"{before_count:,}")
metric_after.metric("전처리 후 행 수", "처리 중")

with st.expander("1단계. CSV 읽기", expanded=True):
    st.success(f"CSV 읽기 완료: {before_count:,}행, {len(raw_df.columns)}열")
    preview(raw_df)

try:
    require_columns(raw_df, raw_required_columns)

    selected_columns = [
        raw_address,
        raw_sido_code,
        raw_type,
        raw_industry,
        raw_members,
        raw_charge,
        raw_company_name,
        raw_status,
        raw_new_members,
        raw_lost_members,
    ]

    df = raw_df[selected_columns].copy()
    with st.expander("2단계. 필요한 컬럼 선택"):
        st.success(f"필요한 컬럼 선택 완료: {len(df.columns)}열")
        preview(df)

    rename_map = {
        raw_company_name: "company_name",
        raw_status: "status_code",
        raw_address: "address",
        raw_sido_code: "sido_code",
        raw_type: "type_code",
        raw_industry: "industry",
        raw_members: "member_count",
        raw_charge: "charge_amount",
        raw_new_members: "new_members",
        raw_lost_members: "lost_members",
    }
    df = df.rename(columns=rename_map)

    with st.expander("3단계. 컬럼명 영문 변경"):
        st.success(f"영문 컬럼명 변경 완료: {len(df.columns)}열")
        preview(df)

    df["status_code"] = (
        df["status_code"].astype("string").str.strip().replace({"1": "등록", "2": "탈퇴"})
    )
    df["status"] = df["status_code"]

    df["type_code"] = (
        df["type_code"].astype("string").str.strip().replace({"1": "법인", "2": "개인"})
    )
    df["company_type"] = df["type_code"]
    df = df.drop(columns=["status_code", "type_code"])

    with st.expander("4단계. 코드값을 텍스트로 변환"):
        st.success("status, company_type 변환 완료")
        preview(df)

    df["sido"] = df["address"].astype("string").str.split().str[0]
    df = df.drop(columns=["address", "sido_code"])

    with st.expander("5단계. 시도명 추출"):
        st.success("시도명 추출 및 불필요 주소 컬럼 제거 완료")
        preview(df)

    for column in ["member_count", "charge_amount", "new_members", "lost_members"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    with st.expander("6단계. 숫자 컬럼 타입 변환"):
        st.success("숫자 컬럼 변환 완료 (변환 실패값은 0)")
        preview(df)

    df["estimated_salary_total"] = df["charge_amount"] / 0.095
    df["estimated_salary_per"] = (
        df["estimated_salary_total"].where(df["member_count"] != 0, 0)
        / df["member_count"].where(df["member_count"] != 0)
    )
    df["estimated_salary_per"] = df["estimated_salary_per"].fillna(0)
    df["net_change"] = df["new_members"] - df["lost_members"]

    with st.expander("7단계. 파생 컬럼 생성"):
        st.success("추정 월급여 및 순증감 컬럼 생성 완료")
        preview(df)

    df = df[
        (df["status"] == "등록")
        & (df["member_count"] != 0)
        & (df["charge_amount"] != 0)
    ].copy()

    with st.expander("8단계. 이상값 처리"):
        st.success(f"등록 사업장 필터링 및 0값 제거 완료: {len(df):,}행")
        preview(df)

    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    df.to_csv(CLEANED_DATA_PATH, encoding="utf-8", index=False)
    metric_after.metric("전처리 후 행 수", f"{len(df):,}")

    with st.expander("9단계. 전처리 결과 저장"):
        st.success(
            f"cleaned_pension.csv 저장 완료 ({len(df):,}행, {len(df.columns)}열)"
        )
        st.caption(CLEANED_DATA_PATH)
        preview(df)

    st.subheader("전처리된 데이터 기본 통계")
    stat_company, stat_sido, stat_members, stat_salary = st.columns(4)
    stat_company.metric("총 사업장 수", f"{len(df):,}")
    stat_sido.metric("시도 수", f"{df['sido'].nunique(dropna=True):,}")
    stat_members.metric("총 가입자 수", f"{df['member_count'].sum():,.0f}")
    stat_salary.metric(
        "전체 1인당 추정 평균 월급여",
        f"{df['estimated_salary_per'].mean():,.0f}",
    )
except Exception as exc:
    metric_after.metric("전처리 후 행 수", "실패")
    st.error(f"전처리 중 오류가 발생했습니다: {exc}")
