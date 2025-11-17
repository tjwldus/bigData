# traffic_app.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="교통사고 데이터 분석", layout="wide")

# -----------------------------
# 데이터 불러오기
# -----------------------------

def load_data():
    df = pd.read_csv("한국도로교통공단_시도시군구별교통사고통계.csv", encoding="cp949")
    return df

df = load_data()

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.image("logo.png", use_container_width=True)
menu = st.sidebar.selectbox(
    "메뉴를 선택하세요",
    ["HOME", "시도별 분석", "시군구별 분석", "상세 비교 분석", "사망률/경상률 분석"]
)
st.sidebar.markdown("---")
st.sidebar.info("데이터 출처: 공공데이터포털\n한국도로교통공단_시도 시군구별 교통사고 통계")

# -----------------------------
# HOME
# -----------------------------
if menu == "HOME":
    st.title("🚗 교통사고 데이터 분석 대시보드")
    st.markdown("""
    **데이터 출처:** [공공데이터포털 - 한국도로교통공단_시도 시군구별 교통사고 통계](https://www.data.go.kr/data/15070339/fileData.do)

    이 앱은 시도 및 시군구별 교통사고 통계를 기반으로
    지역별 사고 규모, 사망자 수, 부상자 현황 등을 시각화한 분석 대시보드입니다.
    """)
    st.image("road.jpg", use_container_width=True)

    st.metric(label="총 사고건수", value=f"{df['사고건수'].sum():,}건")
    st.metric(label="총 사망자수", value=f"{df['사망자수'].sum():,}명")
    st.metric(label="총 중상자수", value=f"{df['중상자수'].sum():,}명")

# -----------------------------
# 시도별 분석
# -----------------------------
elif menu == "시도별 분석":
    st.header("🚦 시도별 교통사고 통계")
    city_summary = df.groupby("시도", as_index=False).sum(numeric_only=True)

    # 데이터프레임 보기
    st.dataframe(city_summary)

    # Plotly 막대 그래프
    fig = px.bar(
        city_summary,
        x="시도",
        y="사고건수",
        text="사고건수",
        title="시도별 교통사고 건수",
        color="사고건수",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 사망자 비율
    fig2 = px.pie(city_summary, values="사망자수", names="시도", title="시도별 사망자 비율")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 시군구별 분석
# -----------------------------
elif menu == "시군구별 분석":
    st.header("🏙️ 시군구별 교통사고 통계")

    selected_city = st.selectbox("시도를 선택하세요", df["시도"].unique())
    filtered = df[df["시도"] == selected_city]

    st.dataframe(filtered)

    fig3 = px.bar(
        filtered.sort_values("사고건수", ascending=False),
        x="시군구",
        y="사고건수",
        color="사고건수",
        title=f"{selected_city} 내 시군구별 교통사고 건수",
        text="사고건수"
    )
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 상세 비교 분석
# -----------------------------
elif menu == "상세 비교 분석":
    st.header("📊 시도 간 상세 비교 분석")

    selected = st.multiselect("비교할 시도를 선택하세요", df["시도"].unique(), default=["서울", "경기"])

    if selected:
        comp = df[df["시도"].isin(selected)].groupby("시도", as_index=False).sum(numeric_only=True)
        st.dataframe(comp)

        fig4 = px.bar(
            comp.melt(id_vars="시도", value_vars=["사고건수", "사망자수", "중상자수", "경상자수", "부상신고자수"]),
            x="시도", y="value", color="variable",
            barmode="group", title="시도별 교통사고 현황 비교"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("비교할 시도를 선택하세요.")


# -----------------------------
# 사망률 vs 경상률 분석
# -----------------------------
if menu == "사망률/경상률 분석":
    st.header("⚡ 사망률 vs 경상률 비교 산점도")
    st.markdown("""
    이 탭은 지역별 사고 양상을 분석합니다.  
    - **사망률**: 사고 1건당 사망자 비율  
    - **경상률**: 사고 1건당 경상자 비율
    """)
    
    # 사망률, 경상률 계산
    df["사망률"] = df["사망자수"] / df["사고건수"]
    df["경상률"] = df["경상자수"] / df["사고건수"]

    # 시도별 선택
    selected_states = st.multiselect(
        "분석할 시도를 선택하세요",
        df["시도"].unique(),
        default=df["시도"].unique()[:5]  # 기본값 5개
    )

    if selected_states:
        filtered = df[df["시도"].isin(selected_states)]

        # 산점도 시각화
        fig = px.scatter(
            filtered,
            x="경상률",
            y="사망률",
            color="시도",
            hover_data=["시군구", "사고건수", "사망자수", "경상자수"],
            size="사고건수",  # 사고건수에 따라 점 크기 조정
            title="지역별 사망률 vs 경상률 비교 산점도"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("분석할 시도를 선택해주세요.")