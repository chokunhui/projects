import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="🍽️ 레스토랑 팁 분석")

tips = sns.load_dataset("tips")

st.title("🍽️ 레스토랑 팁 분석")

st.subheader("섹션 1. 기술 통계 요약")
metric_columns = st.columns(4)
average_tip_rate = (tips["tip"] / tips["total_bill"] * 100).mean()

metric_columns[0].metric("총 데이터 수", f"{len(tips):,}")
metric_columns[1].metric("평균 식사 금액", f"${tips['total_bill'].mean():.2f}")
metric_columns[2].metric("평균 팁 금액", f"${tips['tip'].mean():.2f}")
metric_columns[3].metric("평균 팁 비율", f"{average_tip_rate:.2f}%")

st.dataframe(tips.describe(), use_container_width=True)

st.subheader("섹션 2. 금액 vs 팁 산점도")
scatter_color_options = {
    "성별(sex)": "sex",
    "흡연여부(smoker)": "smoker",
    "요일(day)": "day",
    "시간대(time)": "time",
}
bar_group_options = {
    "요일(day)": "day",
    "성별(sex)": "sex",
    "시간대(time)": "time",
    "흡연여부(smoker)": "smoker",
}

with st.sidebar:
    scatter_color_label = st.selectbox(
        "산점도 색상 기준", list(scatter_color_options)
    )
    bar_group_label = st.selectbox("막대차트 그룹 기준", list(bar_group_options))

scatter_fig = px.scatter(
    tips,
    x="total_bill",
    y="tip",
    color=scatter_color_options[scatter_color_label],
    hover_data=["total_bill", "tip", "size"],
    trendline="ols",
    labels={"total_bill": "식사 금액 ($)", "tip": "팁 금액 ($)"},
)
st.plotly_chart(scatter_fig, use_container_width=True)

st.subheader("섹션 3. 조건별 합계 막대차트")
bar_group_column = bar_group_options[bar_group_label]
bill_totals = (
    tips.groupby(bar_group_column, observed=True)["total_bill"]
    .sum()
    .reset_index()
)
bar_fig = px.bar(
    bill_totals,
    x=bar_group_column,
    y="total_bill",
    text="total_bill",
    title="선택 기준별 총 식사 금액 합계",
    labels={bar_group_column: bar_group_label, "total_bill": "식사 금액 합계 ($)"},
)
bar_fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
st.plotly_chart(bar_fig, use_container_width=True)
