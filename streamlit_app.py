import datetime
import pandas as pd
import requests
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="過去気象データ分析アプリ",
    page_icon="🌤️",
    layout="wide"
)

# 主要都市の緯度・経度リスト
LOCATIONS = {
    "札幌 (北海道)": {"lat": 43.0621, "lon": 141.3544},
    "仙台 (宮城)": {"lat": 38.2682, "lon": 140.8694},
    "東京 (東京都)": {"lat": 35.6895, "lon": 139.6917},
    "横浜 (神奈川)": {"lat": 35.4437, "lon": 139.6380},
    "金沢 (石川)": {"lat": 36.5947, "lon": 136.6256},
    "名古屋 (愛知)": {"lat": 35.1815, "lon": 136.9066},
    "大阪 (大阪府)": {"lat": 34.6937, "lon": 135.5023},
    "広島 (広島)": {"lat": 34.3853, "lon": 132.4553},
    "高松 (香川)": {"lat": 34.3401, "lon": 134.0433},
    "福岡 (福岡)": {"lat": 33.5904, "lon": 130.4017},
    "鹿児島 (鹿児島)": {"lat": 31.5966, "lon": 130.5571},
    "那覇 (沖縄)": {"lat": 26.2124, "lon": 127.6809},
}

# --- Open-Meteo Archive API からデータ取得 ---
@st.cache_data(ttl=3600)
def fetch_weather_data(lat: float, lon: float, start_date: datetime.date, end_date: datetime.date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "sunshine_duration",
            "relative_humidity_2m_mean"
        ],
        "timezone": "Asia/Tokyo"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            daily = data.get("daily", {})
            
            # 秒単位で返る日照時間を時間に変換 (秒 / 3600)
            sunshine_hours = [
                round(s / 3600, 1) if s is not None else 0.0 
                for s in daily.get("sunshine_duration", [])
            ]
            
            df = pd.DataFrame({
                "日付": daily.get("time", []),
                "平均気温 (°C)": daily.get("temperature_2m_mean", []),
                "降水量 (mm)": daily.get("precipitation_sum", []),
                "日照時間 (時間)": sunshine_hours,
                "平均湿度 (%)": daily.get("relative_humidity_2m_mean", [])
            })
            df["日付"] = pd.to_datetime(df["日付"]).dt.date
            return df
        else:
            return None
    except Exception as e:
        st.error(f"データ通信エラーが発生しました: {e}")
        return None


# --- サイドバー (条件設定) ---
st.sidebar.header("⚙️ 取得条件")

selected_location = st.sidebar.selectbox("地域を選択", list(LOCATIONS.keys()))
lat = LOCATIONS[selected_location]["lat"]
lon = LOCATIONS[selected_location]["lon"]

# 過去気象APIの確定データの都合上、2日前までをデフォルト上限に設定
today = datetime.date.today()
max_allowed_date = today - datetime.timedelta(days=2)
default_start = max_allowed_date - datetime.timedelta(days=30)

date_range = st.sidebar.date_input(
    "期間を選択",
    value=(default_start, max_allowed_date),
    max_value=max_allowed_date
)

# 日付選択のバリデーション
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.info("開始日と終了日の両方を選択してください。")
    st.stop()


# --- メインコンテンツ ---
st.title("🌤️ 過去気象データ分析アプリ")
st.caption(f"選択地域: **{selected_location}** （{start_date} ～ {end_date}）")

with st.spinner("気象データを取得中..."):
    df = fetch_weather_data(lat, lon, start_date, end_date)

if df is None or df.empty:
    st.error("指定された期間のデータを取得できませんでした。条件を変更してください。")
    st.stop()

# 期間日数の計算
days_count = len(df)

# --- 1. データサマリー (指標表示) ---
st.subheader("📊 期間内の集計結果")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_precip = df["降水量 (mm)"].sum()
    avg_precip = df["降水量 (mm)"].mean()
    st.metric(
        label="🌧️ 降水量",
        value=f"{total_precip:.1f} mm",
        delta=f"日平均 {avg_precip:.1f} mm"
    )

with col2:
    total_sun = df["日照時間 (時間)"].sum()
    avg_sun = df["日照時間 (時間)"].mean()
    st.metric(
        label="☀️ 日照時間",
        value=f"{total_sun:.1f} 時間",
        delta=f"日平均 {avg_sun:.1f} 時間"
    )

with col3:
    avg_temp = df["平均気温 (°C)"].mean()
    max_temp = df["平均気温 (°C)"].max()
    min_temp = df["平均気温 (°C)"].min()
    st.metric(
        label="🌡️ 期間平均気温",
        value=f"{avg_temp:.1f} °C",
        delta=f"最高 {max_temp:.1f} / 最低 {min_temp:.1f}"
    )

with col4:
    avg_humidity = df["平均湿度 (%)"].mean()
    st.metric(
        label="💧 期間平均湿度",
        value=f"{avg_humidity:.1f} %"
    )

st.divider()

# --- 2. 日別推移グラフ ---
st.subheader("📈 日別推移グラフ")

tab1, tab2, tab3 = st.tabs(["気温・湿度", "降水量", "日照時間"])

with tab1:
    st.line_chart(df.set_index("日付")[["平均気温 (°C)", "平均湿度 (%)"]])

with tab2:
    st.bar_chart(df.set_index("日付")["降水量 (mm)"])

with tab3:
    st.bar_chart(df.set_index("日付")["日照時間 (時間)"])

st.divider()

# --- 3. 詳細データテーブル & ダウンロード ---
st.subheader("📋 詳細データ")

st.dataframe(df, use_container_width=True)

# CSVダウンロード用リンク
csv_data = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 気象データをCSVダウンロード",
    data=csv_data,
    file_name=f"weather_{selected_location}_{start_date}_{end_date}.csv",
    mime="text/csv"
)
